"""Reject actual argument, dictionary-key, optional-value and result mistakes."""
from dronecan import DATATYPES, TYPENAMES
from dronecan.dsdl.parser import CompoundType
from dronecan.transport import CompoundValue, Frame, Transfer, bits_from_bytes


def invalid(datatype: CompoundType, value: CompoundValue, frame: Frame, transfer: Transfer) -> None:
    DATATYPES.get(('341', CompoundType.KIND_MESSAGE))  # E
    TYPENAMES[341]  # E
    descriptor: str = DATATYPES[(341, CompoundType.KIND_MESSAGE)]  # E
    wrong_crc: str = datatype.base_crc  # E
    wrong_bits: str = datatype.get_min_bitlen()  # E
    datatype.get_max_bitlen_response('argument')  # E
    CompoundType('example.Bad', 'message', 'file', 1, (0, 0), '')  # E
    datatype(_mode=123)  # E
    unguarded: CompoundValue = datatype()  # E
    Frame('identifier', b'payload')  # E
    Frame(1, 'payload')  # E
    Frame(1, b'', canfd='yes')  # E
    bits_from_bytes('binary string')  # E
    bits_from_bytes([b'byte'])  # E
    bad_bits_result: bytes = bits_from_bytes(b'byte')  # E
    wrong_frame_data: str = frame.bytes  # E
    definite_transfer_id: tuple[int, int] = frame.transfer_key  # E
    frame.message_id = 'id'  # E
    Transfer(transfer_id='id')  # E
    Transfer(payload=b'already serialized')  # E
    Transfer(canfd='yes')  # E
    wrong_frames: bytes = transfer.to_frames()  # E
    transfer.from_frames([b'not a Frame'])  # E
    transfer.message_id = 'identifier'  # E
    transfer.payload = object()  # E
    definite_payload: CompoundValue = transfer.payload  # E
    wrong_unpack_result: bytes = value._unpack('00000000', True)  # E
    value._unpack(b'not bit text', True)  # E
    transfer.is_response_to(frame)  # E
    print(descriptor, wrong_crc, wrong_bits, unguarded, bad_bits_result, wrong_frame_data, definite_transfer_id, wrong_frames, definite_payload, wrong_unpack_result)
