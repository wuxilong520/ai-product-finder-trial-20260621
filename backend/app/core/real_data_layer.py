from __future__ import annotations


class RealDataManager:
    def detect_state(self, records: list[dict]) -> dict:
        if not records:
            return {
                'data_source_type': 'mock',
                'is_real_platform_data': False,
                'data_confidence_hint': 0.0,
            }
        real_count = sum(1 for item in records if item.get('is_real_platform_data') is True)
        partial_count = sum(1 for item in records if item.get('data_source_type') == 'partial')
        if real_count == len(records):
            return {
                'data_source_type': 'real',
                'is_real_platform_data': True,
                'data_confidence_hint': 1.0,
            }
        if real_count > 0 or partial_count > 0:
            return {
                'data_source_type': 'partial',
                'is_real_platform_data': False,
                'data_confidence_hint': 0.5,
            }
        return {
            'data_source_type': 'mock',
            'is_real_platform_data': False,
            'data_confidence_hint': 0.0,
        }


real_data_manager = RealDataManager()
