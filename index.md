
# Introduction {.unnumbered}

The service **cs2bim** transforms GIS-based cadastral survey (CS) data to IFC instances. The service offers sophisticated options for data model transformation between GIS and IFC, and it provides various methods for geometric conversions, particularly from 2D to 3D.  

The service contains the following major components:  

- Reading 2D GIS feature types and systematically converting them to IFC entities, supporting key concept templates of IFC.
- Processing of the terrain model to create the resulting 3D surfaces with geometric projection methods.
- Processing of CityGML data (buildings) to convert it to IFC entities.
- Processing of 2.5D utility network data to convert it to IFC entities with geometric extrusion methods.
- Exporting of the objects to IFC format using the IfcOpenShell component.
- API access

To run the service, a ready-to-use Docker-based setup is provided.  

These pages describe the technical aspects and configurations of the application, as well as the concepts required and used for it.  

The source code is available on [github](https://github.com/idibau/cs2bim/)  


## Project
This application was originally developed as part of the **cs2bim** project. The project has been launched by the Conference of Cantonal Geoinformation and Cadastral Offices (KGK) as *Cadastral Surveying Data to Building Information Modeling (CS2BIM)*. The _Institute of Virtual Design and Construction_ and the
_Institute of Geomatics_ at the University of Applied Sciences Northwestern Switzerland (FHNW) have developed the service 
based on open source libraries. 

## Authors
[Institut Digitales Bauen](https://www.fhnw.ch/idibau)  
Fachhochschule Nordwestschweiz /  
University of Applied Sciences and Arts Northwestern Switzerland, Institute of Virtual Design and Construction

Project team:  

- Lukas Schildknecht
- Oliver Schneider
- Joel Gschwind
- Jonas Meyer
- Christian Gamma
  
If you use this project for your research, please cite:

```
  @inproceedings{schildknecht2025cs2bim,
    author={Schildknecht, Lukas and Schneider, Oliver and Meyer, Jonas, and Gamma, Christian and Gwschind, Joel},
    title={Integration of land administration data into BIM/IFC - an open source approach for Swiss cadastral survey data},
    year={2025},
    booktitle={Dreiländertagung der DGPF, der OVG und der SGPF in Muttenz, Schweiz},
    series={Publikationen der DGPF},
    volume={Band 33},
    editor={Kersten, Thomas P. and Tilly, Nora},
    publisher={Deutsche Gesellschaft für Photogrammetrie, Fernerkundung und Geoinformation (DGPF) e.V.},
    address={Stuttgart, Germany},
    pages={294--310}
  }
```

## License
BY-NC-SA  
[![](uploads/by-nc-sa.png){width=120px}](https://creativecommons.org/licenses/by-nc-sa/4.0/)
