{
  Double_t energy[700];
  Double_t xsec[700];
  Double_t al[700];
  Double_t fe54[700];
  Double_t fe56[700];
  Double_t fe58[700];
  Double_t ni[700];
  Double_t ti[700];
  Double_t v[700];
  Double_t zr[700];
  Double_t cd[700];
  Double_t au[700];
  Double_t cu[700];
  Double_t in[700];

  Int_t cd_bool = 1;

  //string foil[50] = {"Al","Fe54","Fe56","Fe58","Ni","Ti","V","Zr","Au","Cu","In113"};
  string foil[50] = {"Al", "Fe54", "Fe56", "Fe58", "Zr", "Cu", "cd_case"};

  TTree *etree = new TTree("etree","etree");
  etree->ReadFile("energy.txt","eng1/D:eng2/D:eng3/D:eng4/D:eng5/D:eng6/D:eng7/D:eng8/D");
  Int_t n = etree->GetEntries();
  for (Int_t i=0;i<n;i++) {
    etree->GetEntry(i);
    energy[8*i] = etree->GetLeaf("eng1")->GetValue();
    energy[8*i+1] = etree->GetLeaf("eng2")->GetValue();
    energy[8*i+2] = etree->GetLeaf("eng3")->GetValue();
    energy[8*i+3] = etree->GetLeaf("eng4")->GetValue();
    energy[8*i+4] = etree->GetLeaf("eng5")->GetValue();
    energy[8*i+5] = etree->GetLeaf("eng6")->GetValue();
    energy[8*i+6] = etree->GetLeaf("eng7")->GetValue();
    energy[8*i+7] = etree->GetLeaf("eng8")->GetValue();
  }
  energy[640] = 20;

  TTree *cdtree = new TTree("cdtree","cdtree");
  cdtree->ReadFile("cd_case.txt","cd1/D:cd2/D:cd3/D:cd4/D:cd5/D:cd6/D:cd7/D:cd8/D");
  Int_t n_cd = cdtree->GetEntries();
  for (Int_t i=0;i<n_cd;i++) {
	  cdtree->GetEntry(i);
	  cd[8*i] = cdtree->GetLeaf("cd1")->GetValue();
	  cd[8*i+1] = cdtree->GetLeaf("cd2")->GetValue();
	  cd[8*i+2] = cdtree->GetLeaf("cd3")->GetValue();
	  cd[8*i+3] = cdtree->GetLeaf("cd4")->GetValue();
	  cd[8*i+4] = cdtree->GetLeaf("cd5")->GetValue();
	  cd[8*i+5] = cdtree->GetLeaf("cd6")->GetValue();
	  cd[8*i+6] = cdtree->GetLeaf("cd7")->GetValue();
	  cd[8*i+7] = cdtree->GetLeaf("cd8")->GetValue();
  }

  //Int_t nf = 11;
  Int_t nf = 6;
  for (Int_t j=0;j<nf;j++) {
    TTree *tree = new TTree("tree","tree");
    tree->ReadFile((foil[j] + ".txt").c_str(),"a1/D:a2/D:a3/D:a4/D:a5/D:a6/D:a7/D:a8/D");
    for (Int_t i=0;i<n;i++) {
      tree->GetEntry(i);
      xsec[8*i] = tree->GetLeaf("a1")->GetValue();
      xsec[8*i+1] = tree->GetLeaf("a2")->GetValue();
      xsec[8*i+2] = tree->GetLeaf("a3")->GetValue();
      xsec[8*i+3] = tree->GetLeaf("a4")->GetValue();
      xsec[8*i+4] = tree->GetLeaf("a5")->GetValue();
      xsec[8*i+5] = tree->GetLeaf("a6")->GetValue();
      xsec[8*i+6] = tree->GetLeaf("a7")->GetValue();
      xsec[8*i+7] = tree->GetLeaf("a8")->GetValue();
    }
    /*
    if (cd_bool == 1){
	for (Int_t i=0;i<640;i++) {
		xsec[i] = xsec[i]*exp(-cd[i]*2.354E-3);
	}
    }
    */
    for (Int_t i=0;i<640;i++) {
      cout << xsec[i] << ", ";
    }
    cout << endl;
    if (j == 0) {std::copy(xsec,xsec+700,al);}
    else {
      /*
      if (j == 1) {std::copy(xsec,xsec+700,fe54);}
      if (j == 2) {std::copy(xsec,xsec+700,fe56);}
      if (j == 3) {std::copy(xsec,xsec+700,fe58);}
      if (j == 4) {std::copy(xsec,xsec+700,ni);}
      if (j == 5) {std::copy(xsec,xsec+700,ti);}
      if (j == 6) {std::copy(xsec,xsec+700,v);}
      if (j == 7) {std::copy(xsec,xsec+700,zr);}
      if (j == 8) {std::copy(xsec,xsec+700,au);}
      if (j == 9) {std::copy(xsec,xsec+700,cu);}
      if (j == 10) {std::copy(xsec,xsec+700,in);}
      */
      if (j == 1) {std::copy(xsec,xsec+700,fe54);}
      if (j == 2) {std::copy(xsec,xsec+700,fe56);}
      if (j == 3) {std::copy(xsec,xsec+700,fe58);}
      if (j == 4) {std::copy(xsec,xsec+700,zr);}
      if (j == 5) {std::copy(xsec,xsec+700,cu);}
      if (j == 6) {std::copy(xsec,xsec+700,cd);}
    }
    tree->Delete();
  }

  TH1D *al_h = new TH1D("al_h","al_h",640,energy);
  TH1D *fe54_h = new TH1D("fe54_h","fe54_h",640,energy);
  TH1D *fe56_h = new TH1D("fe56_h","fe56_h",640,energy);
  TH1D *fe58_h = new TH1D("fe58_h","fe58_h",640,energy);
  TH1D *ni_h = new TH1D("ni_h","ni_h",640,energy);
  TH1D *ti_h = new TH1D("ti_h","ti_h",640,energy);
  TH1D *v_h = new TH1D("v_h","v_h",640,energy);
  TH1D *zr_h = new TH1D("zr_h","zr_h",640,energy);
  TH1D *au_h = new TH1D("au_h","au_h",640,energy);
  TH1D *cu_h = new TH1D("cu_h","cu_h",640,energy);
  TH1D *in_h = new TH1D("in_h","in_h",640,energy);
  TH1D *cd_h = new TH1D("cd_h","cd_h",640,energy);

  for (Int_t i=0;i<640;i++) {
    al_h->Fill(energy[i],al[i]);
    fe54_h->Fill(energy[i],fe54[i]);
    fe56_h->Fill(energy[i],fe56[i]);
    fe58_h->Fill(energy[i],fe58[i]);
    //ni_h->Fill(energy[i],ni[i]);
    //ti_h->Fill(energy[i],ti[i]);
    //v_h->Fill(energy[i],v[i]);
    zr_h->Fill(energy[i],zr[i]);
    //au_h->Fill(energy[i],au[i]);
    cu_h->Fill(energy[i],cu[i]);
    //in_h->Fill(energy[i],in[i]);
    cd_h->Fill(energy[i],cd[i]);
  }
/*
  al_h->Scale(1);
  fe54_h->Scale(1);
  fe56_h->Scale(1);
  ni_h->Scale(1);
  ti_h->Scale(1);
  v_h->Scale(1);
  zr_h->Scale(1);
  au_h->Scale(1);
  cu_h->Scale(1);
  in_h->Scale(1);
*/
  TCanvas *c = new TCanvas("c","c",500,350);
  c->SetLogy();
  c->SetLogx();
  if (cd_bool == 1) {
  	al_h->SetTitle("Normalized Foil Cross Sections");
  } 
  else {
	//al_h->SetTitle("Foil Cross Sections");
	al_h->SetTitle("Normalized Foil Cross Sections (bn)");
  }
  al_h->GetYaxis()->SetRangeUser(10E-6,10);
  //al_h->GetYaxis()->SetTitle("Cross Section (bn)");
  al_h->GetYaxis()->SetTitle("Relative Cross Section");
  al_h->GetXaxis()->SetTitle("Neutron Energy (MeV)");
  al_h->SetTitleOffset(1.2);
  al_h->SetStats(0);

  al_h->SetLineColor(7);
  fe54_h->SetLineColor(2); 
  fe56_h->SetLineColor(3); 
  fe58_h->SetLineColor(4);
  zr_h->SetLineColor(5); 
  cu_h->SetLineColor(6); 
  cd_h->SetLineColor(1);

  al_h->SetLineWidth(1);
  fe54_h->SetLineWidth(1);
  fe56_h->SetLineWidth(1);
  fe58_h->SetLineWidth(1);
  zr_h->SetLineWidth(1);
  cu_h->SetLineWidth(1);
  cd_h->SetLineWidth(1);

  //cd_h->SetLineStyle(7);

  al_h->DrawNormalized("hist");
  fe54_h->DrawNormalized("samehist");
  fe56_h->DrawNormalized("samehist");
  fe58_h->DrawNormalized("samehist");
  //ni_h->DrawNormalized("samehist");
  //ti_h->DrawNormalized("samehist");
  //v_h->DrawNormalized("samehist");
  zr_h->DrawNormalized("samehist");
  //au_h->DrawNormalized("samehist");
  cu_h->DrawNormalized("samehist");
  //in_h->DrawNormalized("samehist");
  cd_h->DrawNormalized("samehist");
/*
  al_h->Draw("hist");
  fe54_h->Draw("samehist");
  fe56_h->Draw("samehist");
  ni_h->Draw("samehist");
  ti_h->Draw("samehist");
  v_h->Draw("samehist");
  zr_h->Draw("samehist");
  au_h->Draw("samehist");
  cu_h->Draw("samehist");
  in_h->Draw("samehist");
*/
  leg = new TLegend(0.45,0.7,0.9,0.9);
  leg->SetNColumns(2);
  leg->AddEntry("al_h","Al27(n,#alpha)Na24","l");
  leg->AddEntry("fe54_h","Fe54(n,p)Mn54","l");
  leg->AddEntry("fe56_h","Fe56(n,p)Mn56","l");
  leg->AddEntry("fe58_h","Fe58(n,#gamma)Fe59","l");
  //leg->AddEntry("ni_h","Ni","l");
  //leg->AddEntry("ti_h","Ti","l");
  //leg->AddEntry("v_h","V","l");
  leg->AddEntry("zr_h","Zr90(n,2n)Zr89","l");
  //leg->AddEntry("au_h","Au","l");
  leg->AddEntry("cu_h","Cu63(n,#gamma)Cu64","l");
  //leg->AddEntry("in_h","In 113","l");
  leg->AddEntry("cd_h","Cd Absorption Spectrum","l");
  leg->SetTextSize(0.027);
  leg->Draw();
  
}

  
