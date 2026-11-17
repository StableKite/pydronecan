"""Use genuine registry, parser, frame and transfer objects with finite types."""
from typing import assert_type

from dronecan import DATATYPES, TYPENAMES
from dronecan.dsdl.parser import CompoundType
from dronecan.transport import CompoundValue, Frame, Transfer, bits_from_bytes


def consume() -> None:
    assert_type(DATATYPES, dict[tuple[int, int], CompoundType])
    assert_type(TYPENAMES, dict[str, CompoundType])
    datatype = DATATYPES[(341, CompoundType.KIND_MESSAGE)]
    assert_type(datatype.default_dtid, int | None)
    assert_type(datatype.kind, int)
    assert_type(datatype.base_crc, int)
    assert_type(datatype.get_min_bitlen(), int)
    assert_type(datatype.get_max_bitlen(), int)
    assert_type(datatype.get_data_type_signature(), int)
    value = datatype()
    assert_type(value, CompoundValue | None)
    assert isinstance(value, CompoundValue)
    outgoing = Transfer(transfer_id=7, source_node_id=42, payload=value)
    assert_type(outgoing.payload, bytearray | CompoundValue | None)
    frames = outgoing.to_frames()
    assert_type(frames, list[Frame])
    for frame in frames:
        assert_type(frame.message_id, int)
        assert_type(frame.bytes, bytearray)
        assert_type(frame.transfer_key, tuple[int, int | None])
        assert_type(frame.toggle, bool)
        assert_type(bits_from_bytes(frame.bytes), str)
    incoming = Transfer()
    incoming.from_frames(frames)
    assert isinstance(incoming.payload, CompoundValue)
    assert incoming.payload._type is datatype
    assert_type(incoming.payload._unpack(bits_from_bytes(bytes(7)), True), str)
    incoming.payload = value
    incoming.ts_monotonic = 1.5
    incoming.ts_real = 2.5
    incoming.data_type_id = datatype.default_dtid
    incoming.data_type_crc = datatype.base_crc
    incoming.data_type_signature = datatype.get_data_type_signature()
    incoming.message_id = outgoing.message_id
    assert_type(incoming.is_response_to(outgoing), bool)
    service = TYPENAMES['uavcan.protocol.GetNodeInfo']
    assert service.kind == CompoundType.KIND_SERVICE
    assert_type(service.get_min_bitlen_request(), int)
    assert_type(service.get_max_bitlen_response(), int)
    request = service(_mode='request')
    assert isinstance(request, CompoundValue)
    assert_type(request._pack(), str)
    # The raw descriptor's factory is genuinely an initial no-op until loaded.
    raw = CompoundType('example.Message', CompoundType.KIND_MESSAGE, 'example/1.Message.uavcan', 1, (0, 0), '')
    assert raw() is None
    empty = Frame(1, b'')
    assert empty.transfer_key == (1, None)


if __name__ == '__main__':
    consume()
