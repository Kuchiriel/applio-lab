# venv do dono (~/kvenv) + LD p/ NixOS. source antes de tudo.
export LD_LIBRARY_PATH=/nix/store/3lpf2hl979sfmyb9f573xq1bz3xkds0v-cuda-merged-12.9/lib:/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
export LABPY=$HOME/kvenv/bin/python
mkdir -p /tmp/opencode && ln -sfn ~/kvenv /tmp/opencode/kvenv 2>/dev/null
