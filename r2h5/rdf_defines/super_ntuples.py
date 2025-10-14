def ftag_pileup_trackVariables(df):
    df = df.Define("iPV", "getPrimaryVertexIndex(RecoVtx_isHS)")
    df = df.Define("Track_minDz_PUvtx", "getMinDeltaZ(Track_z0, RecoVtx_z, iPV, true)")
    df = df.Define("Track_minDzsig_PUvtx", "getMinZ0Significance(Track_z0, Track_var_z0, RecoVtx_z, iPV, true)")
    df = df.Define("Track_minDz_PUvtx_dz", "getMinDeltaZSignificance_dZPVVtx(Track_z0, Track_var_z0, RecoVtx_z, iPV, true)")
    df = df.Define("Track_minDz_PUvtx_dzsig", "getMinDeltaZSignificance_dZPVVtxSignificance(Track_minDz_PUvtx_dz, Track_var_z0)")
    df = df.Define("Track_NVtxIn1sig", "getNVtxInZ0Significance(RecoVtx_z, Track_z0, Track_var_z0, 1.0)")
    df = df.Define("Track_NVtxIn3sig", "getNVtxInZ0Significance(RecoVtx_z, Track_z0, Track_var_z0, 3.0)")
    df = df.Define("Track_NVtxIn5sig", "getNVtxInZ0Significance(RecoVtx_z, Track_z0, Track_var_z0, 5.0)")

    # Track selection used in GN2HL training: https://gitlab.cern.ch/atlas-flavor-tagging-tools/training-dataset-dumper/-/blob/main/configs/fragments/ip3d-upgrade-loose-track-cuts.json
    df = df.Define("Track_GN2HL_selection", "getGN2HLSelection(Track_btagIp_d0, Track_btagIp_z0SinTheta, Track_pt, Track_eta, Track_quality)")
    return df

def ftag_pileup_jetTruthVariables(df):
    df = df.Define("AntiKt4EMTopoJets_ConstituentCategory", "getJetConstituentCategory(AntiKt4EMTopoJets_btagTrack_idx, Track_ftagTruthOriginLabel, Track_GN2HL_selection)")
    df = df.Define("AntiKt4EMTopoJets_EnhancedTruthLabelID", "getJetEnhancedTruthLabelID(AntiKt4EMTopoJets_HadronConeExclTruthLabelID, AntiKt4EMTopoJets_pt, AntiKt4EMTopoJets_eta, AntiKt4EMTopoJets_phi, TruthHSJet_pt, TruthHSJet_eta, TruthHSJet_phi)")
    df = df.Define("AntiKt4EMTopoJets_Pt20GeV", "getJetPassSelection(AntiKt4EMTopoJets_pt, 20)")
    return df

def timing_variables(df):
    # Truth HS vertex variables
    df = df.Define("HSvertex_time", "getHSVertexVariable(TruthVtx_time, TruthVtx_isHS)")
    df = df.Define("HSvertex_x", "getHSVertexVariable(TruthVtx_x, TruthVtx_isHS)")
    df = df.Define("HSvertex_y", "getHSVertexVariable(TruthVtx_y, TruthVtx_isHS)")
    df = df.Define("HSvertex_z", "getHSVertexVariable(TruthVtx_z, TruthVtx_isHS)")
    df = df.Define("HSvertex_reco_x", "getHSVertexVariable(RecoVtx_x, RecoVtx_isHS)")
    df = df.Define("HSvertex_reco_y", "getHSVertexVariable(RecoVtx_y, RecoVtx_isHS)")
    df = df.Define("HSvertex_reco_z", "getHSVertexVariable(RecoVtx_z, RecoVtx_isHS)")

    df = df.Define("Cell_above_2GeV", "getCellAboveThreshold(Cell_e, 2.0)")
    df = df.Define("Cell_above_1GeV", "getCellAboveThreshold(Cell_e, 1.0)")

    df = df.Define("Cell_above_4_significance", "getCellAboveThreshold(Cell_significance, 4.0)")
    df = df.Define("Sig_above_3_celle_above_1GeV", "getBothAreOne(getCellAboveThreshold(Cell_e, 1.0), getCellAboveThreshold(Cell_significance, 3.0))")
    df = df.Define("Sig_above_4_celle_above_1GeV", "getBothAreOne(getCellAboveThreshold(Cell_e, 1.0), getCellAboveThreshold(Cell_significance, 4.0))")


    df = df.Define("Cell_time_TOF_corrected", "getCellTimeTOFCorrected_4ml(Cell_time, Cell_x, Cell_y, Cell_z, HSvertex_reco_x, HSvertex_reco_y, HSvertex_reco_z)")
    df = df.Define("Track_isGoodFromHS", "getTrackIsGoodFromHS(Track_quality, Track_ftagTruthOriginLabel)")
    # df = df.Define("Track_isGoodFromHS_old_files", "getTrackIsGoodFromHS(Track_quality, Track_ftagTruthOrigin)")
    df = df.Define("Track_eta_IsGoodwithin_2p5", "getTrackIsGoodwithinEta(Track_quality, Track_eta, 2.5)")
    df = df.Define("Track_above_1GeV", "getTrackAboveThreshold(Track_pt, 1.0)")

    df = df.Define("AntiKt4EMTopoJets_selected", 
                   "getJetSelection(AntiKt4EMTopoJets_pt, AntiKt4EMTopoJets_truthHSJet_idx, 30.0)")

    return df
