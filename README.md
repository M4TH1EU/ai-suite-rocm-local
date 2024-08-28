# ai-suite-rocm-local

This is a simple project to make hosting multiple AI tools easily on Linux with AMD GPUs using ROCM locally (without docker).

> [!WARNING]
> Currently rewriting this project to be more modular and easier to use. This is a work in progress.
> Instructions below outdated !

To use you have to clone the repo run the install script for the service you want to use.

```bash
git clone https://git.broillet.ch/mathieu/ai-suite-rocm-local.git
cd ai-suite-rocm-local/<service name>/
./install.sh
```

Then you can run whichever service you want using their respectives run.sh scripts.

```bash
./run.sh
```



*This has been tested on Fedora 40 with kernel 6.9.6 with an AMD RX 6800 XT.*

