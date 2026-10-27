# Run on a Windows laptop

Use Ubuntu under WSL for the Linux `/proc` metrics and Linux socket tools.

1. If Ubuntu/WSL is already installed, open Ubuntu and skip installation.
2. Otherwise open PowerShell **as Administrator**, run `wsl --install -d Ubuntu`, and restart if prompted. Complete Ubuntu's first-run username/password setup.
3. In Ubuntu, verify `python3 --version`. If needed install the tools with `sudo apt update` then `sudo apt install python3 curl iproute2`.
4. Extract the project on Windows. A Windows path such as `C:\Users\YOUR_NAME\Downloads\linux-operations-lab` is accessible from Ubuntu at `/mnt/c/Users/YOUR_NAME/Downloads/linux-operations-lab`.
5. Run `cd /mnt/c/Users/YOUR_NAME/Downloads/linux-operations-lab`, adjusting the path to your actual folder, then follow README commands using `python3`.
6. Open generated HTML via Windows File Explorer. WSL localhost access varies by setup; all diagnostic curl commands should run inside Ubuntu.

Installing WSL may require virtualization support and administrator access. On a managed university laptop, follow its software-installation policy. Native Linux users do not need WSL.

Official setup reference: https://learn.microsoft.com/en-us/windows/wsl/install
