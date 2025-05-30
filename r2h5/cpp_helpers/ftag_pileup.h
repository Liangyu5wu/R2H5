// helpers.hpp
#include <cmath>
#include <vector>
#include <algorithm>

//using VecF = std::vector<float>;
using VecF = ROOT::VecOps::RVec<float>;
using VecVecF = ROOT::VecOps::RVec<VecF>;
using VecI = ROOT::VecOps::RVec<int>;
using VecVecI = ROOT::VecOps::RVec<VecI>;

int getPrimaryVertexIndex(const VecI& recovertex_isHS) {
    // Loop over recovertex_isHS to find the first hard-scatter vertex
    for (size_t i = 0; i < recovertex_isHS.size(); ++i) {
        if (recovertex_isHS[i] == 1) {  // Assuming 1 indicates a hard-scatter vertex
            return i;  // Return the index of the primary vertex
        }
    }
    return -1;  // Return -1 if no hard-scatter vertex is found
}

VecF getMinDeltaZ(const VecF& track_z0, const VecF& vertex_z, const int iPV=-1, bool excludePV=false) {
    if (track_z0.empty() || vertex_z.empty()) return {};
    
    VecF min_track_z0;
    for (const auto& z_track : track_z0) {
        float min_dz = 1e3;
        float signed_min_dz = 1e3;
        for (const auto& z_vertex : vertex_z) {
            if (iPV != -1 && excludePV && z_vertex == vertex_z[iPV]) continue;
            else if (iPV != -1 && !excludePV && z_vertex != vertex_z[iPV]) continue;
            double dz = std::abs(z_track - z_vertex);
            if (dz < min_dz) {
                min_dz = dz;
                signed_min_dz = z_track - z_vertex;
            }
        }
        min_track_z0.push_back(signed_min_dz); // convert to mm
    }
    return min_track_z0;
}


VecF getMinZ0Significance(const VecF& track_z0, const VecF& track_z0_var, const VecF& vertex_z, const int iPV=-1, bool excludePV=false) {
    if (track_z0.empty() || track_z0_var.empty() || vertex_z.empty()) return {};
    
    VecF min_z0_sig;
    for (size_t i = 0; i < track_z0.size(); i++) {
        float min_z0_sig_i = 1e3;
        for (const auto& z_vertex : vertex_z) {
            if (iPV != -1 && excludePV && z_vertex == vertex_z[iPV]) continue;
            else if (iPV != -1 && !excludePV && z_vertex != vertex_z[iPV]) continue;
            double z0_sig_i = (track_z0[i] - z_vertex) / sqrt(track_z0_var[i]);
            if (abs(z0_sig_i) < abs(min_z0_sig_i)) {
                min_z0_sig_i = z0_sig_i;
            }
        }
        min_z0_sig.push_back(min_z0_sig_i);
    }
    return min_z0_sig;
}

VecF getMinDeltaZSignificance_dZPVVtx(const VecF& track_z0, const VecF& track_z0_var, const VecF& vertex_z, const int iPV=-1, bool excludePV=false) {
    if (track_z0.empty() || track_z0_var.empty() || vertex_z.empty()) return {};
    
    float min_dz_sig = 1e3;
    float dz_vtx_PV = 1e6;
    VecF mindzsig_dzVtxPV;
    for (size_t i = 0; i < track_z0.size(); i++) {
        for (const auto& z_vertex : vertex_z) {
            if (iPV != -1 && excludePV && z_vertex == vertex_z[iPV]) continue;
            else if (iPV != -1 && !excludePV && z_vertex != vertex_z[iPV]) continue;
            double dz = std::abs(track_z0[i] - z_vertex);
            double dz_sig = dz / sqrt(track_z0_var[i]);
            if (dz_sig < min_dz_sig) {
                min_dz_sig = dz_sig;
                dz_vtx_PV = z_vertex - vertex_z[iPV];
            }
        }
        mindzsig_dzVtxPV.push_back(dz_vtx_PV);
    }
    return mindzsig_dzVtxPV;
}

VecF getMinDeltaZSignificance_dZPVVtxSignificance(const VecF& mindzsig_dzVtxPV, const VecF& track_z0_var) {
    if (mindzsig_dzVtxPV.empty() || track_z0_var.empty()) return {};
    
    VecF mindzsig_dzVtxPV_sig;
    for (size_t i = 0; i < mindzsig_dzVtxPV.size(); i++) {
        float dz_sig = mindzsig_dzVtxPV[i];
        float dz_sig_sig = dz_sig / sqrt(track_z0_var[i]);
        mindzsig_dzVtxPV_sig.push_back(dz_sig_sig);
    }
    return mindzsig_dzVtxPV_sig;
}

VecI getNVtxInZ0Significance(const VecF& recovertex_z, const VecF& track_z0, const VecF& track_z0_var, const float significance_cut) {
    if (recovertex_z.empty() || track_z0.empty() || track_z0_var.empty()) return {};
    
    VecI n_vtx_in_z0_sig;
    for (size_t i = 0; i < track_z0.size(); i++) {
        int n_vtx = 0;
        for (const auto& z_vertex : recovertex_z) {
            double z0_sig = (track_z0[i] - z_vertex) / sqrt(track_z0_var[i]);
            if (abs(z0_sig) < significance_cut) {
                n_vtx++;
            }
        }
        n_vtx_in_z0_sig.push_back(n_vtx);
    }
    return n_vtx_in_z0_sig;
}

VecI getGN2HLSelection(const VecF& track_d0, const VecF& track_z0SinTheta, const VecF& track_pt, const VecF& track_eta, const VecI& track_quality) {
    if (track_d0.empty() || track_z0SinTheta.empty() || track_pt.empty() || track_eta.empty() || track_quality.empty()) return {};
    
    VecI gn2hl_selection;
    for (size_t i = 0; i < track_d0.size(); i++) {
        if (std::abs(track_d0[i]) <= 3.5 && std::abs(track_z0SinTheta[i]) < 5.0 && track_pt[i] >= 0.5 && std::abs(track_eta[i]) <= 4.0 && track_quality[i] == 1) {
            gn2hl_selection.push_back(1);
        } else {
            gn2hl_selection.push_back(0);
        }
    }
    return gn2hl_selection;
}

VecI getJetConstituentCategory(const VecVecI& jet_constituent_idx, const VecI& track_truth_origin_label, const VecI& track_gn2hl_selection) {
    if (jet_constituent_idx.empty() || track_truth_origin_label.empty() || track_gn2hl_selection.empty()) return {};
    
    VecI jet_constituent_category;
    for (const auto& track_indices : jet_constituent_idx) {
        int jet_category = 3; // No secondary tracks
        for (const auto& track_idx : track_indices) {
            if (!track_gn2hl_selection[track_idx]) continue; // Skip if not selected

            int track_truth = track_truth_origin_label[track_idx];
            if ((track_truth == 3) || (track_truth == 4)) {
                jet_category = 0; // Has B-tracks
            }
            else if (!(jet_category == 0) && (track_truth == 5)) {
                jet_category = 1; // Has C-tracks
            }
            else if (!(jet_category <= 1) && (track_truth >= 6)) {
                jet_category = 2; // Has Tau/OtherSecondary tracks
            }
        }
        jet_constituent_category.push_back(jet_category);
    }
    return jet_constituent_category;
}

//    df = df.Define("AntiKt4EMTopoJets_EnhancedTruthLabelID", "getJetEnhancedTruthLabelID(AntiKt4EMTopoJets_HadronConeExclTruthLabelID, AntiKt4EMTopoJets_pt, AntiKt4EMTopoJets_eta, AntiKt4EMTopoJets_phi, TruthHSJet_pt, TruthHSJet_eta, TruthHSJet_phi)")
/* This function returns a detailed jet label based on the following criteria, considering isolation w.r.t. other jets and overlap with truth jets with a threshold of 20 GeV
    0: Light jet with no reco-level b-jets within 0.1 cone
    1: Light jet with a reco-level b-jet within 0.1 cone, where only 1 jet is found in a cone of 1.0 around 
    2: Light jet with a reco-level b-jet within 0.1 cone, where there are two truth jets in a cone of 1.0 around the point at the center of the two jets
    3: Light jet with a reco-level b-jet within 0.1 cone, where there are at least three truth jets in a cone of 1.0 around the point at the center of the three jets
    4: Charm jet
    5: Bottom jet
*/
VecI getJetEnhancedTruthLabelID(const VecI& jet_truth_label, const VecF& jet_pt, const VecF& jet_eta, const VecF& jet_phi, const VecF& truth_jet_pt, const VecF& truth_jet_eta, const VecF& truth_jet_phi) {
    if (jet_truth_label.empty() || jet_pt.empty() || jet_eta.empty() || jet_phi.empty() || truth_jet_pt.empty() || truth_jet_eta.empty() || truth_jet_phi.empty()) return {};
    
    VecI enhanced_truth_label;
    for (size_t i = 0; i < jet_truth_label.size(); i++) {
        int label = jet_truth_label[i];
        if (label == 0) {
            int j_bjet = -1;
            for (size_t j = 0; j < jet_pt.size(); j++) {
                if (j == i) continue; // Skip the same jet
                if (jet_truth_label[j] != 5) continue; // Skip non-b-jets
                float dR = std::sqrt(std::pow(jet_eta[i] - jet_eta[j], 2) + std::pow(jet_phi[i] - jet_phi[j], 2));
                if (dR < 0.1) {
                    label = 1; // Light jet with a reco-level b-jet within 0.1 cone
                    j_bjet = j;
                    break;
                }
            }
            if (j_bjet != -1) {
                int n_truth_jets = 0;
                float center_eta = (jet_eta[i] + jet_eta[j_bjet]) / 2.0;
                float center_phi = (jet_phi[i] + jet_phi[j_bjet]) / 2.0;
                for (size_t j = 0; j < truth_jet_pt.size(); j++) {
                    if (truth_jet_pt[j] < 20.0) continue; // Skip low pt truth jets
                    float dR = std::sqrt(std::pow(center_eta - truth_jet_eta[j], 2) + std::pow(center_phi - truth_jet_phi[j], 2));
                    if (dR < 1.0) {
                        n_truth_jets++;
                    }
                }
                if (n_truth_jets == 1) label = 1; 
                else if (n_truth_jets == 2) label = 2; 
                else if (n_truth_jets >= 3) label = 3;
            }
        }
        enhanced_truth_label.push_back(label);
    }
    return enhanced_truth_label;
}

VecI getJetPassSelection(const VecF& jet_pt, const float pt_cut) {
    if (jet_pt.empty()) return {};
    
    VecI pass_selection;
    for (const auto& pt : jet_pt) {
        if (pt > pt_cut) {
            pass_selection.push_back(1);
        } else {
            pass_selection.push_back(0);
        }
    }
    return pass_selection;
}