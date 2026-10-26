Prepared for Minecraft Forge 1.20.1 using Forge's OBJ model loader.
atm.obj and trade_kiosk.obj preserve the source mesh and UV coordinates, with geometry normalized to fit within a 1-block footprint and 2-block height.
The JSON files are loader descriptors, not vanilla blockstate files. Textures and matching MTL files are intentionally not generated; add those after texture artwork is ready.
For use inside a mod, place OBJ files under assets/<modid>/models/ and update each JSON model path to match that mod's resource location.
