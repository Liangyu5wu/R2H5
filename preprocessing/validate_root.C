#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cmath>
#include <TFile.h>
#include <TTree.h>
#include <TInterpreter.h>

void validate_first_file() {
    // Generate dictionaries for vector<vector<int>> and vector<vector<float>>
    gInterpreter->GenerateDictionary("vector<vector<int> >", "vector");
    gInterpreter->GenerateDictionary("vector<vector<float> >", "vector");
    
    // Open the first ROOT file
    std::string filename = "/fs/ddn/sdf/group/atlas/d/liangyu/jetML/SuperNtuple_mu200/user.scheong.43348828.Output._000001.SuperNtuple.root";
    
    TFile *file = TFile::Open(filename.c_str(), "READ");
    if (!file || file->IsZombie()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    
    std::cout << "Successfully opened file: " << filename << std::endl;

    TTree *tree = nullptr;
    file->GetObject("ntuple", tree);
    if (!tree) {
        std::cerr << "Error getting TTree 'ntuple' from file" << std::endl;
        file->Close();
        return;
    }

    // Set up necessary branches
    std::vector<float> *truthVtxTime = nullptr;
    std::vector<float> *truthVtxX = nullptr;
    std::vector<float> *truthVtxY = nullptr;
    std::vector<float> *truthVtxZ = nullptr;
    std::vector<bool> *truthVtxIsHS = nullptr;
    std::vector<float> *recoVtxX = nullptr;
    std::vector<float> *recoVtxY = nullptr;
    std::vector<float> *recoVtxZ = nullptr;
    std::vector<bool> *recoVtxIsHS = nullptr;
    std::vector<float> *topoJetsPt = nullptr;
    std::vector<float> *topoJetsEta = nullptr;
    std::vector<float> *topoJetsPhi = nullptr;
    std::vector<float> *topoJetsWidth = nullptr;
    std::vector<std::vector<int>> *topoJets_TruthHSJetIdx = nullptr;
    int eventNumber = 0;

    tree->SetBranchAddress("TruthVtx_time", &truthVtxTime);
    tree->SetBranchAddress("TruthVtx_x", &truthVtxX);
    tree->SetBranchAddress("TruthVtx_y", &truthVtxY);
    tree->SetBranchAddress("TruthVtx_z", &truthVtxZ);
    tree->SetBranchAddress("TruthVtx_isHS", &truthVtxIsHS);
    tree->SetBranchAddress("RecoVtx_x", &recoVtxX);
    tree->SetBranchAddress("RecoVtx_y", &recoVtxY);
    tree->SetBranchAddress("RecoVtx_z", &recoVtxZ);
    tree->SetBranchAddress("RecoVtx_isHS", &recoVtxIsHS);
    tree->SetBranchAddress("AntiKt4EMTopoJets_pt", &topoJetsPt);
    tree->SetBranchAddress("AntiKt4EMTopoJets_eta", &topoJetsEta);
    tree->SetBranchAddress("AntiKt4EMTopoJets_phi", &topoJetsPhi);
    tree->SetBranchAddress("AntiKt4EMTopoJets_width", &topoJetsWidth);
    tree->SetBranchAddress("AntiKt4EMTopoJets_truthHSJet_idx", &topoJets_TruthHSJetIdx);
    tree->SetBranchAddress("eventNumber", &eventNumber);

    std::cout << "Total entries in tree: " << tree->GetEntries() << std::endl;
    std::cout << "\n=== Processing first 5 events ===" << std::endl;

    // Process only first 5 events
    Long64_t maxEntries = std::min((Long64_t)5, tree->GetEntries());
    
    for (Long64_t entry = 0; entry < maxEntries; ++entry) {
        tree->GetEntry(entry);
        
        std::cout << "\n--- Event " << entry << " (eventNumber: " << eventNumber << ") ---" << std::endl;
        
        // Find HS vertex information
        float hsVtxTime = -999.0;
        float hsVtxX = -999.0, hsVtxY = -999.0, hsVtxZ = -999.0;
        float recoHsVtxX = -999.0, recoHsVtxY = -999.0, recoHsVtxZ = -999.0;
        bool foundHsVtx = false;
        bool foundRecoHsVtx = false;
        
        // Truth HS vertex
        if (truthVtxIsHS && truthVtxTime && truthVtxX && truthVtxY && truthVtxZ) {
            for (size_t i = 0; i < truthVtxIsHS->size(); ++i) {
                if (truthVtxIsHS->at(i)) {
                    hsVtxTime = truthVtxTime->at(i);
                    hsVtxX = truthVtxX->at(i);
                    hsVtxY = truthVtxY->at(i);
                    hsVtxZ = truthVtxZ->at(i);
                    foundHsVtx = true;
                    break;
                }
            }
        }
        
        // Reco HS vertex
        if (recoVtxIsHS && recoVtxX && recoVtxY && recoVtxZ) {
            for (size_t i = 0; i < recoVtxIsHS->size(); ++i) {
                if (recoVtxIsHS->at(i)) {
                    recoHsVtxX = recoVtxX->at(i);
                    recoHsVtxY = recoVtxY->at(i);
                    recoHsVtxZ = recoVtxZ->at(i);
                    foundRecoHsVtx = true;
                    break;
                }
            }
        }
        
        std::cout << "HS Vertex Info:" << std::endl;
        if (foundHsVtx) {
            std::cout << "  Truth HS vertex: time=" << std::fixed << std::setprecision(3) 
                     << hsVtxTime << "ps, pos=(" << hsVtxX << ", " << hsVtxY << ", " << hsVtxZ << ")" << std::endl;
        } else {
            std::cout << "  No truth HS vertex found!" << std::endl;
        }
        
        if (foundRecoHsVtx) {
            std::cout << "  Reco HS vertex: pos=(" << recoHsVtxX << ", " << recoHsVtxY << ", " << recoHsVtxZ << ")" << std::endl;
            if (foundHsVtx) {
                float distance = std::sqrt((hsVtxX - recoHsVtxX)*(hsVtxX - recoHsVtxX) +
                                         (hsVtxY - recoHsVtxY)*(hsVtxY - recoHsVtxY) +
                                         (hsVtxZ - recoHsVtxZ)*(hsVtxZ - recoHsVtxZ));
                std::cout << "  Truth-Reco distance: " << distance << " mm" << std::endl;
            }
        } else {
            std::cout << "  No reco HS vertex found!" << std::endl;
        }
        
        // Apply jet selection logic (mimicking getJetSelection function)
        std::cout << "\nJet Selection:" << std::endl;
        
        if (!topoJetsPt) {
            std::cout << "  ERROR: topoJetsPt is null!" << std::endl;
            continue;
        }
        
        std::cout << "  Total jets in event: " << topoJetsPt->size() << std::endl;
        
        std::vector<int> selectedJetIndices;
        
        for (size_t j = 0; j < topoJetsPt->size(); ++j) {
            float jetPt = topoJetsPt->at(j);
            bool passes_pt_cut = (jetPt > 30.0);  // From getJetSelection in timing.h
            
            bool has_truth_match = false;
            if (topoJets_TruthHSJetIdx && j < topoJets_TruthHSJetIdx->size()) {
                has_truth_match = !topoJets_TruthHSJetIdx->at(j).empty();
            }
            
            bool passes_selection = passes_pt_cut && has_truth_match;
            
            float jetEta = (topoJetsEta && j < topoJetsEta->size()) ? topoJetsEta->at(j) : -999.0;
            float jetPhi = (topoJetsPhi && j < topoJetsPhi->size()) ? topoJetsPhi->at(j) : -999.0;
            float jetWidth = (topoJetsWidth && j < topoJetsWidth->size()) ? topoJetsWidth->at(j) : -999.0;
            
            std::cout << "    Jet " << j << ": pt=" << std::setprecision(1) << jetPt 
                     << ", eta=" << std::setprecision(3) << jetEta
                     << ", phi=" << jetPhi 
                     << ", width=" << jetWidth
                     << ", pt_cut=" << (passes_pt_cut ? "PASS" : "FAIL")
                     << ", truth_match=" << (has_truth_match ? "YES" : "NO")
                     << ", selected=" << (passes_selection ? "YES" : "NO") << std::endl;
            
            if (passes_selection) {
                selectedJetIndices.push_back(j);
            }
        }
        
        std::cout << "  Selected jets count: " << selectedJetIndices.size() << std::endl;
        
        if (!selectedJetIndices.empty()) {
            std::cout << "  Selected jets details:" << std::endl;
            for (size_t k = 0; k < selectedJetIndices.size(); ++k) {
                int jetIdx = selectedJetIndices[k];
                float jetPt = topoJetsPt->at(jetIdx);
                float jetEta = (topoJetsEta && jetIdx < topoJetsEta->size()) ? topoJetsEta->at(jetIdx) : -999.0;
                float jetPhi = (topoJetsPhi && jetIdx < topoJetsPhi->size()) ? topoJetsPhi->at(jetIdx) : -999.0;
                float jetWidth = (topoJetsWidth && jetIdx < topoJetsWidth->size()) ? topoJetsWidth->at(jetIdx) : -999.0;
                
                std::cout << "    Selected jet " << k << " (original index " << jetIdx << "): "
                         << "pt=" << std::setprecision(1) << jetPt
                         << ", eta=" << std::setprecision(3) << jetEta
                         << ", phi=" << jetPhi
                         << ", width=" << jetWidth << std::endl;
            }
        }
        
        // If exceeding max_objects=20, show truncation info
        if (selectedJetIndices.size() > 20) {
            std::cout << "  NOTE: Will be truncated to 20 jets in H5 file (max_objects=20)" << std::endl;
        }
    }
    
    std::cout << "\n=== Validation completed ===" << std::endl;
    std::cout << "Compare these results with your H5 file:" << std::endl;
    std::cout << "- HSvertex data should match truth HS vertex info" << std::endl;
    std::cout << "- jets data should contain selected jets (up to 20 per event)" << std::endl;
    std::cout << "- Event-to-jets correspondence should be preserved" << std::endl;

    file->Close();
    delete file;
}

int main() {
    validate_first_file();
    return 0;
}
