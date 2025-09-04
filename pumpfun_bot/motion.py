import os
import random
import threading
import time
from typing import Optional

from .config import Settings


class MotionController:
	"""Motion driver that toggles a servo and/or LED while active.

	- On Raspberry Pi with RPi.GPIO available: control SERVO_PIN and/or LED_PIN.
	- Otherwise, acts as a no-op.
	"""

	def __init__(self) -> None:
		self._running = False
		self._thread: Optional[threading.Thread] = None
		self._mode = os.getenv("MOVE_MODE", "servo")
		self._interval_s = max(0.03, int(os.getenv("MOTION_INTERVAL_MS", "120")) / 1000.0)
		self._rng = random.Random()

		# Lazy GPIO fields
		self._gpio = None
		self._pwm = None
		self._led_pin = None
		self._servo_pin = None

	try:
		import RPi.GPIO as GPIO  # type: ignore
		_GPIO_AVAILABLE = True
	except Exception:
		_GPIO_AVAILABLE = False

	def start(self) -> None:
		if self._running:
			return
		self._running = True
		if self._GPIO_AVAILABLE:
			self._setup_gpio()
		self._thread = threading.Thread(target=self._run_loop, daemon=True)
		self._thread.start()

	def stop(self) -> None:
		self._running = False
		if self._thread:
			self._thread.join(timeout=1.5)
			self._thread = None
		self._teardown_gpio()

	def _setup_gpio(self) -> None:
		try:
			import RPi.GPIO as GPIO  # type: ignore
		except Exception:
			return
		self._gpio = GPIO
		GPIO.setmode(GPIO.BCM)
		# LED setup
		try:
			self._led_pin = int(os.getenv("LED_PIN", "17"))
			GPIO.setup(self._led_pin, GPIO.OUT)
		except Exception:
			self._led_pin = None
		# Servo setup
		try:
			self._servo_pin = int(os.getenv("SERVO_PIN", "18"))
			GPIO.setup(self._servo_pin, GPIO.OUT)
			freq = int(os.getenv("SERVO_FREQ", "50"))
			self._pwm = GPIO.PWM(self._servo_pin, freq)
			self._pwm.start(_duty_for_angle(90))
		except Exception:
			self._pwm = None
			self._servo_pin = None

	def _teardown_gpio(self) -> None:
		if not self._GPIO_AVAILABLE or not self._gpio:
			return
		try:
			if self._pwm is not None:
				self._pwm.stop()
			import RPi.GPIO as GPIO  # type: ignore
			GPIO.cleanup()
		except Exception:
			pass
		self._gpio = None
		self._pwm = None
		self._led_pin = None
		self._servo_pin = None

	def _run_loop(self) -> None:
		"""Animate while running. If no GPIO available, just sleep until stop."""
		while self._running:
			if self._gpio is None:
				time.sleep(self._interval_s)
				continue
			if self._mode in ("led", "both") and self._led_pin is not None:
				self._animate_led()
			if self._mode in ("servo", "both") and self._pwm is not None:
				self._animate_servo()
			time.sleep(self._interval_s)

	def _animate_led(self) -> None:
		try:
			val = 1 if self._rng.random() > 0.4 else 0
			self._gpio.output(self._led_pin, val)  # type: ignore[union-attr]
		except Exception:
			pass

	def _animate_servo(self) -> None:
		# Bounce between min and max with some randomness
		try:
			min_angle = int(os.getenv("SERVO_MIN_ANGLE", "35"))
			max_angle = int(os.getenv("SERVO_MAX_ANGLE", "145"))
			angle = self._rng.randint(min_angle, max_angle)
			duty = _duty_for_angle(angle)
			self._pwm.ChangeDutyCycle(duty)  # type: ignore[union-attr]
		except Exception:
			pass


def _duty_for_angle(angle: int) -> float:
	"""Map 0..180 angle to duty cycle using config bounds."""
	min_dc = float(os.getenv("SERVO_MIN_DUTY", "2.5"))
	max_dc = float(os.getenv("SERVO_MAX_DUTY", "12.5"))
	angle = max(0, min(180, angle))
	return min_dc + (max_dc - min_dc) * (angle / 180.0)


