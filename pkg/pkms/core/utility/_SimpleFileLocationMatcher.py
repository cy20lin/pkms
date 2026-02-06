from typing import Iterable,Optional
from ..model import FileLocation
from ._FileLocationMatcher import FileLocationMatcher

class SimpleFileLocationMatcher(FileLocationMatcher):
    def __init__(self, file_locations: Iterable[FileLocation]):
        super().__init__(file_locations=file_locations)
    
    def reset(self, file_locations: Iterable[FileLocation]):
        return super().do_reset(file_locations=file_locations)

    def find_match_index(self, file_location: FileLocation) -> Optional[int]:
        best_index = None
        best_len = -1

        for i, candidate_file_location in enumerate(self.file_locations):
            if candidate_file_location.scheme != file_location.scheme:
                continue
            if candidate_file_location.authority != file_location.authority:
                continue
            candidate_segments = candidate_file_location.segments
            target_segments = file_location.segments
            if len(candidate_segments) > len(target_segments):
                continue

            if target_segments[:len(candidate_segments)] == candidate_segments:
                if len(candidate_segments) > best_len:
                    best_len = len(candidate_segments)
                    best_index = i

        return best_index

    def find_match(self, file_location: FileLocation) -> Optional[FileLocation]:
        index = self.find_match_index(file_location)
        return self.file_locations[index] if index is not None else None