import os

for i in range(1,9):
    if i == 6:
        continue
    os.system("python3 zoom_on_swimmer.py --json videos/2021_Chartres_dos_hommes_200_serieRap.json --videog /home/amigo/Bureau/data/chartres_2021/200dos_m_serieRap.mov --videod /home/amigo/Bureau/data/chartres_2021/200dos_m_serieRap1.mov " +
               "--out /home/amigo/Bureau/data/chartres_2021/zoom_200_" + str(i) + ".mp4 "
               + "--csv videos/2021_Chartres_dos_hommes_200_serieRap_manuel_2.csv --type_data manuel "
               + "--lane " + str(i)
               )
