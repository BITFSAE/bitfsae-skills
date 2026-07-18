# Embedded Firmware and Interface Standards

## Contents

1. Source of truth
2. STM32 and generated code
3. CAN and DBC
4. Other hardware interfaces
5. Common configuration
6. Timing, interrupts, and failure handling
7. Verification

## 1. Source of Truth

Cross-check claims in this order, adjusting for the repository:

1. approved system interface database or hardware design;
2. generator input such as `.ioc`;
3. application source and public headers;
4. generated source;
5. prose documents.

When these disagree, determine whether generation is stale, custom code intentionally overrides generated values, or the document is wrong. Do not silently choose one.

## 2. STM32 and Generated Code

- Change clocks, pins, peripherals, DMA, NVIC, and generator-owned settings in CubeMX or the appropriate generator input.
- Put custom additions to generated C/H files only in preserved user regions.
- Put substantial logic in independent modules with small public headers.
- After regeneration, verify custom source files remain in CMake/IDE build lists, user regions survive, interrupt hooks still call application handlers, and safety-related peripheral settings remain effective.
- Document any intentional post-initialization register correction when the generator output does not match its configuration.
- Verify Debug builds after regeneration; also verify Release for delivery, optimization-sensitive code, or memory changes.

## 3. CAN and DBC

Document bus bitrate, frame type, ID, direction, DLC, period or event trigger, timeout, and owner. For each payload field document byte range, bit range when needed, byte order, signedness, scale, offset, unit, valid range, invalid value, and reset behavior.

Also document:

- command CRC/checksum parameters and calculation range;
- sequence and acknowledgement matching;
- command validity duration and replay/renewal behavior;
- retry, mailbox-full, bus-off, and dropped-frame behavior;
- signal freshness and fallback policy;
- which values are targets versus actual outputs;
- whether configuration is RAM-only or persistent.

Use exact examples and verify their calculations. Provide parsing/packing code in C or the language actually used by the consuming project. Do not add an unrelated scripting-language example merely because it is convenient.

Keep DBC message IDs, lengths, byte order, signedness, scale, units, value tables, node direction, and comments aligned with code. Include received messages as well as transmitted messages when the DBC is meant to describe the node's complete interface. Mark provisional upstream signal names explicitly.

## 4. Other Hardware Interfaces

For UART, I2C, SPI, ADC, PWM, capture, GPIO, and sensors, document the items that a maintainer or integrator must know:

- peripheral instance and pin mapping;
- speed, mode, polarity, pull, electrical inversion, and voltage level;
- address representation, including 7-bit versus HAL-shifted I2C addresses;
- sample rate, filter, conversion time, timeout, and calibration;
- units, signed direction, saturation, and disconnected values;
- physical formulas such as PWM mapping or pulses-per-revolution.

Keep board-specific facts in a hardware document, reusable driver contracts in public headers, and frequently changed application values in a configuration document.

## 5. Common Configuration

Use named definitions for values that are routinely changed: IDs, periods, timeouts, thresholds, calibration, control curves, slew rates, fallback values, and address assignments. Include units in names where practical.

The configuration document must tell a maintainer:

- what can be changed safely;
- where to change it;
- allowed ranges and relationships;
- whether CAN commands can override it;
- whether the override survives reset;
- what interfaces, tests, calibration, or hardware must be updated together.

## 6. Timing, Interrupts, and Failure Handling

Document main-loop periods, interrupt-driven inputs, shared data handling, timeouts, and startup sequencing. Keep interrupt handlers short and transfer substantial work to application code.

For vehicle control and monitoring, define behavior for missing sensors, stale messages, invalid data, peripheral start failure, bus-off, full transmit queues, watchdog reset, and reboot. Prefer bounded waits. Distinguish fail-safe behavior from normal control and from manual test modes.

Do not describe a diagnostic bit without stating when it is set, when it clears, and whether it changes control output.

## 7. Verification

Verify as applicable:

- generator configuration against generated initialization;
- source constants against documentation and DBC;
- example frames, CRCs, signed values, scaling, and invalid markers;
- build inclusion of custom modules;
- Debug and Release builds;
- static warnings and memory use;
- bench cases for startup, nominal operation, missing input, malformed command, timeout, recovery, and reset;
- document links and version-control cleanliness.

Record hardware tests that are still pending in `CHANGELOG.md` rather than implying they passed.
