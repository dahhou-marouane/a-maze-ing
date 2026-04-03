from typing import Dict, Tuple, List
all_data: Dict[str, Dict[str, int | bool | Tuple[int, int] | str | None] | List[List[Dict[str, bool]]] | str | bool | int | List[str]] = {
	'colorado': ['\033[0m', '\033[31m', '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m'],
	'emoji': ['██', '42', '$$', '@@', '##', '🌲', '🍄', '🔥'],
	'emoji2': ['▓▓', '🐭', '🐾', '🌟', '🍬', '💎', '🔮', '🍪', '👣', '42', '@@'],
	'w': -1,
	'wc': -1,
	'p': -1,
	'pc': -1,
    }
all_data['wall_char'] = all_data[['emoji'][0]]
print(all_data['wall_char'])