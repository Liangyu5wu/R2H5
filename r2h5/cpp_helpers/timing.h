// helpers.hpp
#include <cmath>
#include <vector>
#include <algorithm>

//using VecF = std::vector<float>;
using VecF = ROOT::VecOps::RVec<float>;
using VecVecF = ROOT::VecOps::RVec<VecF>;
using VecI = ROOT::VecOps::RVec<int>;
using VecVecI = ROOT::VecOps::RVec<VecI>;
using VecB = ROOT::VecOps::RVec<bool>;
const double c_light = 0.299792458; // speed of light in vacuum in mm/ps

VecB getTrackIsGoodFromHS(VecB &trackQuality, VecI &truthOrigin) {
    VecB trackIsGood;
    for (size_t i = 0; i < trackQuality.size(); i++) {
        if (trackQuality[i] && truthOrigin[i] != 0) {
            trackIsGood.push_back(true);
        } else {
            trackIsGood.push_back(false);
        }
    }
    return trackIsGood;
}

VecI getCellAboveThreshold(VecF &cellE, float threshold) {
    VecI cellAboveThreshold;
    for (size_t i = 0; i < cellE.size(); i++) {
        if (cellE[i] > threshold) {
            cellAboveThreshold.push_back(1);
        } else {
            cellAboveThreshold.push_back(0);
        }
    }
    return cellAboveThreshold;
}

VecI getBothAreOne(VecI firstValues, VecI secondValues) {
    VecI bothAreOne;
    for (size_t i = 0; i < std::min(firstValues.size(), secondValues.size()); i++) {
        if (firstValues[i] == 1 && secondValues[i] == 1) {
            bothAreOne.push_back(1);
        } else {
            bothAreOne.push_back(0);
        }
    }
    return bothAreOne;
}

VecI getTrackwithinEta(VecF &track_eta, float threshold) {
    VecI TrackwithinEta;
    for (size_t i = 0; i < track_eta.size(); i++) {
        if (std::abs(track_eta[i]) <= threshold) {
            TrackwithinEta.push_back(1);
        } else {
            TrackwithinEta.push_back(0);
        }
    }
    return TrackwithinEta;
}


float getHSVertexVariable(VecF &truthVtxVariable, VecB &truthVtxIsHS) {
    float hsVertexVariable = 0;
    for (size_t i = 0; i < truthVtxVariable.size(); i++) {
        if (truthVtxIsHS[i]) {
            hsVertexVariable = truthVtxVariable[i];
            break;
        }
    }
    return hsVertexVariable;
}

VecF getCellTimeTOFCorrected_4ml(VecF &cellTime, VecF &cellX, VecF &cellY, VecF &cellZ, float hsVertexX, float hsVertexY, float hsVertexZ) {
    VecF cellTimeTOFCorrected;
    for (size_t i = 0; i < cellTime.size(); i++) {
        float dx = cellX[i] - hsVertexX;
        float dy = cellY[i] - hsVertexY;
        float dz = cellZ[i] - hsVertexZ;
        float distance_vtx_to_cell = std::sqrt(dx * dx + dy * dy + dz * dz);
        float cell_distance_to_origin = std::sqrt(cellX[i] * cellX[i] + cellY[i] * cellY[i] + cellZ[i] * cellZ[i]);
        cellTimeTOFCorrected.push_back(
            cellTime[i] + (cell_distance_to_origin - distance_vtx_to_cell)/c_light
        );
    }
    return cellTimeTOFCorrected;
}

VecF getCellTimeTOFCorrected(VecF &cellTime, VecF &cellX, VecF &cellY, VecF &cellZ,
                              float hsVertexTime, float hsVertexX, float hsVertexY, float hsVertexZ) {
    VecF cellTimeTOFCorrected;
    for (size_t i = 0; i < cellTime.size(); i++) {
        float dx = cellX[i] - hsVertexX;
        float dy = cellY[i] - hsVertexY;
        float dz = cellZ[i] - hsVertexZ;
        float distance_vtx_to_cell = std::sqrt(dx * dx + dy * dy + dz * dz);
        float vtx_distance_to_origin = std::sqrt(cellX[i] * cellX[i] + cellY[i] * cellY[i] + cellZ[i] * cellZ[i]);
        cellTimeTOFCorrected.push_back(
            cellTime[i] + (vtx_distance_to_origin - distance_vtx_to_cell)/c_light - hsVertexTime
        );
    }
    return cellTimeTOFCorrected;
}

VecB getJetSelection(VecF &jet_pt, ROOT::VecOps::RVec<std::vector<int>> &jet_truthHSJet_idx, float threshold) {
    VecB jet_selection;
    
    for (size_t i = 0; i < jet_pt.size(); i++) {
        bool passes_pt_cut = (jet_pt[i] > 30.0);
        
        bool has_truth_match = false;
        if (i < jet_truthHSJet_idx.size()) {
            has_truth_match = !jet_truthHSJet_idx[i].empty();
        }
        
        bool passes_selection = passes_pt_cut && has_truth_match;
        jet_selection.push_back(passes_selection);
    }
    
    return jet_selection;
}
