// Blockbench helper for the ATM/Kiosk OBJ conversion workspace.
// This plugin adds a menu shortcut that opens the built-in OBJ import workflow.
// It intentionally does not alter geometry or generate textures.
let importAction;

Plugin.register('atm_kiosk_obj_helper', {
  title: 'ATM & Kiosk OBJ Helper',
  author: 'RZ17-17',
  description: 'Shortcut and guidance for importing ATM and kiosk OBJ meshes into Blockbench.',
  icon: 'view_in_ar',
  version: '1.0.0',
  min_version: '4.8.0',
  variant: 'both',
  onload() {
    importAction = new Action('atm_kiosk_obj_import_help', {
      name: 'Import ATM / Kiosk OBJ (Help)',
      description: 'Opens instructions for importing the source OBJ model.',
      icon: 'file_upload',
      click() {
        Blockbench.showMessageBox({
          title: 'Import ATM / Kiosk OBJ',
          message: 'Use File → Import → Import OBJ Model, then select ATM.obj or kios jualan.obj. OBJ geometry does not include textures unless the matching MTL and texture files are present.',
          buttons: ['OK']
        });
      }
    });
    MenuBar.addAction(importAction, 'file.import');
  },
  onunload() {
    if (importAction) importAction.delete();
  }
});
