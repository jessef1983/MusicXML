@echo off
echo Cleaning input-xml directory (keeping .gitkeep)...
cd input-xml
for %%f in (*) do (
    if not "%%f"==".gitkeep" (
        if not "%%f"==".gitignore" (
            echo Deleting %%f
            del "%%f"
        )
    )
)
cd ..
echo Input directory cleaned!