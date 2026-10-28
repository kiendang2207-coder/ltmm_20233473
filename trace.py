from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

try:
    from src.mickey2 import clock_kg
except Exception:  # pragma: no cover
    try:
        from .src.mickey2 import clock_kg
    except Exception:  # pragma: no cover
        clock_kg = None

REGISTER_BITS = 100


def bytes_to_bits(data: bytes, nbits: int) -> list[int]:
    """Chuyển byte sang bit theo MSB-first."""
    return [(data[i // 8] >> (7 - i % 8)) & 1 for i in range(nbits)]


def _normalize_register_value(value: Optional[str | Sequence[int]]) -> Optional[str]:
    """Chuẩn hóa trạng thái R/S về dạng chuỗi bit để dễ validate và xuất JSON."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence):
        if not value:
            raise ValueError("register không được rỗng.")
        if any(not isinstance(bit, int) or bit not in (0, 1) for bit in value):
            raise ValueError("register phải là chuỗi bit hoặc list[int] chỉ chứa 0/1.")
        return "".join(str(bit) for bit in value)
    raise TypeError("register phải là chuỗi bit hoặc sequence[int].")


def validate_bit(value: Optional[int], field_name: str) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value not in (0, 1)
    ):
        raise ValueError(f"{field_name} phải là 0, 1 hoặc None; nhận {value!r}.")


def validate_register(
    value: Optional[str | Sequence[int]], field_name: str, strict_register_length: bool
) -> None:
    normalized = _normalize_register_value(value)
    if normalized is None:
        return
    if not normalized or any(bit not in "01" for bit in normalized):
        raise ValueError(f"{field_name} phải là chuỗi không rỗng chỉ gồm 0 và 1.")
    if strict_register_length and len(normalized) != REGISTER_BITS:
        raise ValueError(
            f"{field_name} phải dài {REGISTER_BITS} bit, nhận {len(normalized)} bit."
        )


@dataclass
class TraceEvent:
    """Một sự kiện trace của mỗi bước chạy."""

    sequence: int
    phase: str
    operation: str

    input_bit: Optional[int] = None
    mixing: Optional[bool] = None

    control_bit_r: Optional[int] = None
    control_bit_s: Optional[int] = None

    r_before: Optional[str | list[int]] = None
    s_before: Optional[str | list[int]] = None
    r_after: Optional[str | list[int]] = None
    s_after: Optional[str | list[int]] = None

    keystream_bit: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TraceRecorder:
    """Recorder ghi toàn bộ tiến trình chạy của MICKEY 2.0."""

    def __init__(self, *, strict_register_length: bool = True) -> None:
        self.strict_register_length = strict_register_length
        self._events: list[TraceEvent] = []

    def record_clock_step(
        self,
        *,
        phase: str = "clock",
        operation: str,
        input_bit: Optional[int] = None,
        mixing: Optional[bool] = None,
        control_bit_r: Optional[int] = None,
        control_bit_s: Optional[int] = None,
        r_before: Optional[str | list[int]] = None,
        s_before: Optional[str | list[int]] = None,
        r_after: Optional[str | list[int]] = None,
        s_after: Optional[str | list[int]] = None,
        keystream_bit: Optional[int] = None,
    ) -> TraceEvent:
        """Ghi một bước clock hoặc clock-like step do engine tính toán."""
        return self.record(
            phase=phase,
            operation=operation,
            input_bit=input_bit,
            mixing=mixing,
            control_bit_r=control_bit_r,
            control_bit_s=control_bit_s,
            r_before=r_before,
            s_before=s_before,
            r_after=r_after,
            s_after=s_after,
            keystream_bit=keystream_bit,
        )

    def record(
        self,
        *,
        phase: str,
        operation: str,
        input_bit: Optional[int] = None,
        mixing: Optional[bool] = None,
        control_bit_r: Optional[int] = None,
        control_bit_s: Optional[int] = None,
        r_before: Optional[str | list[int]] = None,
        s_before: Optional[str | list[int]] = None,
        r_after: Optional[str | list[int]] = None,
        s_after: Optional[str | list[int]] = None,
        keystream_bit: Optional[int] = None,
    ) -> TraceEvent:
        """Ghi một sự kiện trace."""
        if not isinstance(phase, str) or not phase.strip():
            raise ValueError("phase không được để trống.")
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation không được để trống.")
        if mixing is not None and not isinstance(mixing, bool):
            raise TypeError("mixing phải là bool hoặc None.")

        bit_fields = {
            "input_bit": input_bit,
            "control_bit_r": control_bit_r,
            "control_bit_s": control_bit_s,
            "keystream_bit": keystream_bit,
        }
        for name, value in bit_fields.items():
            validate_bit(value, name)

        register_fields = {
            "r_before": r_before,
            "s_before": s_before,
            "r_after": r_after,
            "s_after": s_after,
        }
        for name, value in register_fields.items():
            validate_register(value, name, self.strict_register_length)

        event = TraceEvent(
            sequence=len(self._events),
            phase=phase,
            operation=operation,
            input_bit=input_bit,
            mixing=mixing,
            control_bit_r=control_bit_r,
            control_bit_s=control_bit_s,
            r_before=r_before,
            s_before=s_before,
            r_after=r_after,
            s_after=s_after,
            keystream_bit=keystream_bit,
        )
        self._events.append(event)
        return event

    def trace_execution(
        self,
        *,
        key: bytes,
        iv: bytes,
        data: bytes = b"",
        iv_bits: Optional[int] = None,
        note: Optional[str] = None,
    ) -> dict[str, Any]:
        """Ghi toàn bộ tiến trình chạy: init IV -> init key -> preclock -> keystream -> crypt."""
        if clock_kg is None:
            raise RuntimeError("Không thể import clock_kg từ src.mickey2; kiểm tra module path.")
        if len(key) != 10:
            raise ValueError(f"Khóa phải dài 80 bit (10 byte), nhận {len(key)} byte.")
        if iv_bits is None:
            iv_bits = len(iv) * 8
        if not (0 <= iv_bits <= 80 and iv_bits <= len(iv) * 8):
            raise ValueError(f"iv_bits không hợp lệ: {iv_bits}.")

        R = [0] * REGISTER_BITS
        S = [0] * REGISTER_BITS

        def record_step(
            *,
            phase: str,
            operation: str,
            bit_input: Optional[int],
            bit_mixing: Optional[bool],
            r_before: Sequence[int],
            s_before: Sequence[int],
            r_after: Sequence[int],
            s_after: Sequence[int],
            keystream_bit: Optional[int] = None,
        ) -> None:
            ctrl_r = S[34] ^ R[67]
            ctrl_s = S[67] ^ R[33]
            self.record_clock_step(
                phase=phase,
                operation=operation,
                input_bit=bit_input,
                mixing=bit_mixing,
                control_bit_r=ctrl_r,
                control_bit_s=ctrl_s,
                r_before=list(r_before),
                s_before=list(s_before),
                r_after=list(r_after),
                s_after=list(s_after),
                keystream_bit=keystream_bit,
            )

        for bit in bytes_to_bits(iv, iv_bits):
            r_before = list(R)
            s_before = list(S)
            R, S = clock_kg(R, S, True, bit)
            record_step(
                phase="init_iv",
                operation="clock_kg",
                bit_input=bit,
                bit_mixing=True,
                r_before=r_before,
                s_before=s_before,
                r_after=R,
                s_after=S,
            )

        for bit in bytes_to_bits(key, 80):
            r_before = list(R)
            s_before = list(S)
            R, S = clock_kg(R, S, True, bit)
            record_step(
                phase="init_key",
                operation="clock_kg",
                bit_input=bit,
                bit_mixing=True,
                r_before=r_before,
                s_before=s_before,
                r_after=R,
                s_after=S,
            )

        for _ in range(100):
            r_before = list(R)
            s_before = list(S)
            R, S = clock_kg(R, S, True, 0)
            record_step(
                phase="preclock",
                operation="clock_kg",
                bit_input=0,
                bit_mixing=True,
                r_before=r_before,
                s_before=s_before,
                r_after=R,
                s_after=S,
            )

        ciphertext = bytearray()
        for byte_index in range(len(data)):
            byte = 0
            for bit_index in range(8):
                r_before = list(R)
                s_before = list(S)
                ks_bit = (R[0] ^ S[0]) & 1
                R, S = clock_kg(R, S, False, 0)
                record_step(
                    phase="keystream",
                    operation="clock_kg",
                    bit_input=0,
                    bit_mixing=False,
                    r_before=r_before,
                    s_before=s_before,
                    r_after=R,
                    s_after=S,
                    keystream_bit=ks_bit,
                )
                byte = (byte << 1) | ks_bit
            ciphertext_byte = byte ^ data[byte_index]
            ciphertext.append(ciphertext_byte)
            self.record(
                phase="encrypt",
                operation="xor_byte",
            )

        return {
            "ciphertext": bytes(ciphertext),
            "event_count": len(self._events),
            "key_bits": 80,
            "iv_bits": iv_bits,
        }

    def export_json(self, path: str | Path, *, indent: int = 2) -> Path:
        """Xuất toàn bộ trace thành file JSON dạng bảng để dễ đọc."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rows = []
        for event in self._events:
            row = {
                "sequence": event.sequence,
                "phase": event.phase,
                "operation": event.operation,
                "input_bit": event.input_bit,
                "mixing": event.mixing,
                "control_bit_r": event.control_bit_r,
                "control_bit_s": event.control_bit_s,
                "keystream_bit": event.keystream_bit,
                "r_before": event.r_before,
                "s_before": event.s_before,
                "r_after": event.r_after,
                "s_after": event.s_after,
            }
            rows.append(row)

        output_path.write_text(
            json.dumps(rows, indent=indent, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path


def run_demo() -> None:
    """Chạy demo trace cho toàn bộ quá trình."""
    trace = TraceRecorder(strict_register_length=False)
    key = bytes.fromhex("00112233445566778899")
    iv = bytes.fromhex("11223344556677889900")
    data = b"HELLO"
    output_path = Path(__file__).resolve().parent.parent / "trace_demo.json"

    result = trace.trace_execution(key=key, iv=iv, data=data)
    trace.export_json(output_path)
    print(f"\nXuất: {output_path}")
    print(f"Số sự kiện: {result['event_count']}")
    print(f"Mã hóa: {result['ciphertext']!r}")
    print("Dạng JSON: bảng trace.")
    print("Trace chạy theo quy trình MICKEY.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Trace MICKEY đầy đủ."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Chạy demo trace.",
    )
    args = parser.parse_args()
    if args.demo:
        run_demo()
    else:
        parser.print_help()
