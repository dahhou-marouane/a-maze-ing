from typing import List


class DisplayConfig:
    _colorado: List[str] = ['\033[0m', '\033[31m', '\033[91m',
                           '\033[92m', '\033[93m', '\033[94m',
                           '\033[95m', '\033[96m']
    _emoji: List[str] = ['██', '42', '$$', '@@', '##', '🌲', '🍄', '🔥']
    _emoji2: List[str] = ['▓▓', '🐭', '🐾', '🌟',
                         '🍬', '💎', '🔮', '🍪', '👣', '42', '@@']
    wall_char: str = _emoji[0]
    path_char: str = _emoji2[0]
    wall_color: str = ""
    path_color: str = ""
    _w: int = -1
    _wc: int = -1
    _p: int = -1
    _pc: int = -1
    path: bool = False
    old_col: int = 0
    old_rows: int = 0

    def new_wall_colol(self) -> None:
        self._w += 1
        self.wall_color = self._colorado[self._w % len(self._colorado)]

    def new_wall_char(self) -> None:
        self._wc += 1
        self.wall_char = self._emoji[self._w % len(self._emoji)]

    def new_path_colol(self) -> None:
        self._p += 1
        self.path_color = self._colorado[self._p % len(self._colorado)]
    
    def new_path_char(self) -> None:
        self._pc += 1
        self.path_char = self._emoji2[self._pc % len(self._emoji2)]


k = DisplayConfig()
print(k._w)
k.new_wall_colol()
print(k._w)