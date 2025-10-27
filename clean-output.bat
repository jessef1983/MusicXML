@echo off
echo Cleaning output-xml directory (keeping .gitkeep)...
cd output-xml
for %%f in (*) do (
    if not "%%f"==".gitkeep" (
        if not "%%f"==".gitignore" (
            echo Deleting %%f
            del "%%f"
        )
    )
)
cd ..
echo Output directory cleaned!