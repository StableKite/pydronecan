"""Snapshot genuine DSDL signatures and serialized defaults without CAN devices."""
import hashlib
import json
import sys

import dronecan
from dronecan import transport


def snapshot():
    rows = []
    codecs = []
    for name, datatype in sorted(dronecan.TYPENAMES.items()):
        service = datatype.kind == datatype.KIND_SERVICE
        modes = ('request', 'response') if service else (None,)
        signatures = {'name': name, 'kind': datatype.kind, 'default_dtid': datatype.default_dtid, 'version': datatype.version, 'dsdl_signature': datatype.get_dsdl_signature(), 'data_type_signature': datatype.get_data_type_signature()}
        signatures['lengths'] = [datatype.get_min_bitlen_request(), datatype.get_max_bitlen_request(), datatype.get_min_bitlen_response(), datatype.get_max_bitlen_response()] if service else [datatype.get_min_bitlen(), datatype.get_max_bitlen()]
        rows.append(signatures)
        for mode in modes:
            for canfd in (False, True):
                value = datatype(_mode=mode) if service else datatype()
                assert isinstance(value, transport.CompoundValue)
                packed = value._pack(tao=not canfd)
                restored = datatype(_mode=mode) if service else datatype()
                restored._unpack(packed, not canfd)
                assert restored._pack(not canfd) == packed
                row = {'name': name, 'mode': mode, 'canfd': canfd, 'bits': packed}
                if datatype.default_dtid and (datatype.default_dtid, datatype.kind) in dronecan.DATATYPES:
                    sending = transport.Transfer(transfer_id=17, source_node_id=42, dest_node_id=21 if service else None, payload=value, request_not_response=(mode == 'request'), service_not_message=service, canfd=canfd)
                    frames = sending.to_frames()
                    receiving = transport.Transfer()
                    receiving.from_frames(frames)
                    assert isinstance(receiving.payload, transport.CompoundValue)
                    assert receiving.payload._pack(not canfd) == packed
                    row['wire_frames'] = [{'id': frame.message_id, 'bytes': bytes(frame.bytes).hex(), 'canfd': frame.canfd} for frame in frames]
                    row['decoded_bits'] = receiving.payload._pack(not canfd)
                codecs.append(row)
    payload = {'registry': [[key[0], key[1], value.full_name, value.base_crc] for key, value in sorted(dronecan.DATATYPES.items())], 'types': rows, 'codecs': codecs}
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    print(json.dumps({'data': payload, 'canonical_sha256': hashlib.sha256(encoded).hexdigest(), 'types': len(rows), 'registry_entries': len(dronecan.DATATYPES), 'codec_cases': len(codecs), 'actual_package': dronecan.__file__, 'gil_enabled_after': sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else None}, sort_keys=True))


if __name__ == '__main__':
    snapshot()
