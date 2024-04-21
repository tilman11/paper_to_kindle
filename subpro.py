import subprocess

echo = subprocess.Popen(('echo'), stdout=subprocess.PIPE)
proc = subprocess.run(["k2pdfopt", "temp_files/upload/MLOps_1657283700.pdf", "-ui-", "-om", "0.2"], stdin=echo.stdout) #"-w 784", "-h 1135"
proc.wait()
# k2pdfopt MLOps_1657283700.pdf -ui- -om 0.2 –…∞µ~∫√ç≈¥≤å‚∂ƒ©ªº∆@œ‘±•πø⁄¨Ω†®€∑¡“¶¢[]|][¢[]|{{||||{} –æ‘±•¿'–…∞µ