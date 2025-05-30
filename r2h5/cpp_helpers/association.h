#include <vector>

std::vector<std::vector<int>> associate_tracks_to_jets(
    const std::vector<std::vector<int>>& Jet_track_idx,
    int max_jets,
    int max_tracks_per_jet)
{
    std::vector<std::vector<int>> track_associations(max_jets, std::vector<int>(max_tracks_per_jet, -1));

    for (size_t jet_idx = 0; jet_idx < Jet_track_idx.size(); ++jet_idx) {
        if (jet_idx >= max_jets) break;  
        for (size_t track_pos = 0; track_pos < Jet_track_idx[jet_idx].size(); ++track_pos) {
            if (track_pos >= max_tracks_per_jet) break;  
            track_associations[jet_idx][track_pos] = Jet_track_idx[jet_idx][track_pos];
        }
    }
    return track_associations;
}