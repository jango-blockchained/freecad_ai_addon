# Ein vollständiger Leitfaden zur Erstellung eines FreeCAD-Addons: Initialisierung und Icon-Zuweisung

Dieser Bericht bietet eine erschöpfende technische Anleitung zur Erstellung eines FreeCAD-Addons in Python. Der Schwerpunkt liegt auf den grundlegenden, aber entscheidenden Schritten der Initialisierung eines benutzerdefinierten Arbeitsbereichs (Workbench) und der korrekten Zuweisung seines Icons. Die hier dargelegten Methoden und Praktiken entsprechen den Standards, die von den Kernentwicklern von FreeCAD für die Erstellung robuster, wartbarer und performanter Addons empfohlen werden.Die architektonische Grundlage von FreeCAD WorkbenchesBevor mit der Programmierung begonnen wird, ist ein tiefes Verständnis der zugrunde liegenden Architektur von FreeCAD unerlässlich. Die Art und Weise, wie FreeCAD Erweiterungen verwaltet, basiert auf klaren Prinzipien, die die Stabilität und Modularität der Software gewährleisten.Module vs. Workbenches: Eine entscheidende UnterscheidungDie Begriffe "Modul" und "Workbench" werden oft synonym verwendet, bezeichnen aber unterschiedliche Entitäten in der FreeCAD-Architektur. Ein Verständnis dieser Unterscheidung ist der erste Schritt zur korrekten Strukturierung eines Addons.Ein Modul ist jede Erweiterung von FreeCAD. Es kann neue Funktionalitäten, Objekttypen, Import-/Exportformate oder andere Kernfunktionen hinzufügen, ohne notwendigerweise eine grafische Benutzeroberfläche (GUI) zu besitzen.1Eine Workbench (Arbeitsbereich) ist eine spezielle Art von Modul, die eine GUI-Konfiguration bereitstellt. Diese Konfiguration umfasst typischerweise Werkzeugleisten, Menüs und spezielle Bedienfelder, die für eine bestimmte Aufgabe gruppiert sind.1 Wenn ein Benutzer von einem Arbeitsbereich zu einem anderen wechselt, ändert sich die verfügbare Werkzeugpalette, während der Inhalt der 3D-Szene unverändert bleibt.1Ein Entwickler erstellt also nicht einfach eine "Workbench", sondern ein "Modul", das sich der FreeCAD-GUI als Workbench präsentiert. Diese Erkenntnis erklärt, warum bestimmte Initialisierungsdateien auch dann erforderlich sind, wenn sie zunächst leer erscheinen – sie sind für die nicht-visuellen Aspekte des Moduls zuständig.Das App/Gui-Trennungsprinzip: Der Eckpfeiler der FreeCAD-ArchitekturEin zentrales und nicht verhandelbares Prinzip in der FreeCAD-Entwicklung ist die strikte Trennung zwischen Anwendungslogik (App) und grafischer Benutzeroberfläche (Gui).2 FreeCAD ist so konzipiert, dass es auch ohne grafische Oberfläche im Konsolenmodus (FreeCADCmd) ausgeführt werden kann. Dies ermöglicht den Einsatz als leistungsstarke server-seitige Geometrie-Engine oder als Bibliothek in anderen Programmen.3Für einen Addon-Entwickler hat dieses Prinzip direkte Konsequenzen:Die Kernlogik eines Addons (z. B. die Erstellung parametrischer Objekte, Berechnungen, Dateiverarbeitung) darf keine GUI-spezifischen Bibliotheken wie FreeCADGui importieren.Die UI-bezogene Logik (Erstellung von Schaltflächen, Werkzeugleisten, Task-Panels) muss vollständig von der Kernlogik getrennt sein.Dieses Prinzip manifestiert sich direkt in der Notwendigkeit von zwei spezifischen Initialisierungsdateien: Init.py und InitGui.py. Beim Start von FreeCAD durchläuft der Modul-Lader alle verfügbaren Addon-Verzeichnisse und führt diese Skripte in einer bestimmten Reihenfolge aus:Init.py: Diese Datei wird immer ausgeführt, unabhängig davon, ob FreeCAD im GUI- oder im Konsolenmodus startet. Hier werden nicht-visuelle Komponenten wie benutzerdefinierte Import-/Export-Handler oder die Definition von skriptbasierten Objekten registriert.5InitGui.py: Diese Datei wird nur ausgeführt, wenn FreeCAD im GUI-Modus startet (nachdem die Variable App.GuiUp auf 1 gesetzt wurde).6 Hier wird die Workbench selbst definiert, ihre Werkzeugleisten werden erstellt und alle anderen GUI-Elemente werden initialisiert.5Die Existenz dieser beiden Dateien ist also eine direkte Folge des App/Gui-Trennungsprinzips und für die korrekte Funktion eines Addons unerlässlich.Die kanonische Dateistruktur für eine Python-WorkbenchEin FreeCAD-Addon ist im Wesentlichen ein Verzeichnis, das in einem speziellen Mod-Ordner abgelegt wird. Dieser Ordner kann für den aktuellen Benutzer durch Ausführen von App.getUserAppDataDir() + "Mod" in der Python-Konsole von FreeCAD gefunden werden.7Obwohl FreeCAD nur das Vorhandensein von Init.py und InitGui.py erzwingt, hat sich in der Community eine erweiterte, standardisierte Struktur etabliert, die die Organisation, Wartbarkeit und Verteilung von Addons erheblich verbessert.10 Die folgende Tabelle beschreibt die empfohlene Verzeichnisstruktur für ein Beispiel-Addon namens "ProtoWB".Pfad/DateiZweck und detaillierte ErklärungMod/ProtoWB/Das Stammverzeichnis des Workbench-Moduls. Der Name "ProtoWB" wird für unser Beispiel verwendet. Dieses Verzeichnis wird von FreeCAD als ein einzelnes Modul erkannt.Init.pyWird zuerst ausgeführt, sowohl im GUI- als auch im Konsolenmodus. Diese Datei ist für nicht-GUI-Initialisierungen vorgesehen. Für eine einfache Workbench kann diese Datei leer sein, muss aber existieren.InitGui.pyDer Fokus dieses Berichts. Wird nur im GUI-Modus ausgeführt. Hier wird die Workbench-Klasse definiert, ihr Icon und ihr Name werden festgelegt und ihre Werkzeugleisten und Befehle werden bei der FreeCAD-GUI registriert.ProtoWB/Ein Unterverzeichnis mit demselben Namen wie das Stammverzeichnis. Dies ist eine Python-Namespace-Konvention, um den Quellcode der Workbench von den Initialisierungsskripten zu trennen und die Organisation zu verbessern.ProtoWB/commands.pyEine Beispieldatei, die die Python-Klassen für jeden der Befehle der Workbench enthält.icons/Ein dediziertes Verzeichnis zur Speicherung aller Icon-Dateien. Dies ist eine entscheidende Best Practice, um Assets organisiert zu halten.icons/ProtoWB.svgDas primäre Icon für die Workbench selbst. Die Benennung nach der Workbench ist eine starke Konvention.icons/ProtoWB_Command1.svgDas Icon für einen spezifischen Befehl innerhalb der Workbench.resources/Ein Verzeichnis für andere Assets, wie z. B. UI-Dateien (.ui), die mit Qt Designer erstellt wurden, oder Qt-Ressourcendateien (.qrc).README.mdStandard-Dokumentationsdatei, die den Zweck und die Verwendung der Workbench erklärt.package.xmlEine Metadatendatei, die vom FreeCAD Addon Manager verwendet wird, um Informationen über das Addon anzuzeigen, Abhängigkeiten zu verwalten und Updates zu handhaben.11Der Kern der Workbench: Die Erstellung von InitGui.pyDie Datei InitGui.py ist das Herzstück der grafischen Repräsentation einer Workbench. Sie enthält den Code, der FreeCAD anweist, wie der Arbeitsbereich im Menü angezeigt, welche Werkzeuge bereitgestellt und wie er beim Aktivieren initialisiert werden soll.Die Definition der Workbench-KlasseDas zentrale Element in InitGui.py ist eine Python-Klasse, die von einer Basis-Workbench-Klasse erbt. Für in Python geschriebene Workbenches wird eine von FreeCAD bereitgestellte Basisklasse verwendet, die die notwendige Schnittstelle zur GUI implementiert.5Python# Importieren der notwendigen FreeCAD-Module
import FreeCADGui

# Definition der Workbench-Klasse

class ProtoWorkbench(Workbench):
"""
Eine Beispiel-Workbench-Klasse.
"""
#... Klassendefinition folgt hier...
Essenzielle Klassenattribute: Name, Tooltip und IconDie Metadaten, die FreeCAD benötigt, um die Workbench im Auswahlmenü darzustellen, werden als statische Klassenattribute definiert. Dies ist die direkte Antwort auf die Kernanforderungen der Benutzeranfrage.5MenuText: Eine Zeichenkette, die den Namen der Workbench definiert, wie er im Dropdown-Menü der Arbeitsbereiche erscheint.ToolTip: Eine Zeichenkette, die als Beschreibungstext angezeigt wird, wenn der Benutzer mit der Maus über den Namen der Workbench im Menü fährt.Icon: Definiert das Icon für die Workbench. Dies ist ein kritischer Punkt, der in Abschnitt 3 ausführlich behandelt wird.Pythonclass ProtoWorkbench(Workbench):
MenuText = "ProtoWB"
ToolTip = "Ein Prototyp einer Workbench zur Demonstration."
Icon = """ # Hier wird das Icon definiert (siehe Abschnitt 3)
"""
#... weitere Methoden...
Die Lebenszyklus-Methoden der WorkbenchDie Workbench-Klasse verfügt über drei zentrale Methoden, die von FreeCAD zu bestimmten Zeitpunkten in ihrem Lebenszyklus aufgerufen werden: Initialize(), Activated() und Deactivated().5 Ein korrektes Verständnis und die richtige Nutzung dieser Methoden sind entscheidend für die Performance und das korrekte Verhalten des Addons.Initialize(): Diese Methode wird nur ein einziges Mal aufgerufen, wenn das Modul zum ersten Mal geladen wird. Hier sollten die UI-Strukturen wie Werkzeugleisten und Menüs definiert und die Befehlsklassen importiert werden. Um den Start von FreeCAD nicht zu verlangsamen, sollte diese Methode so schlank wie möglich gehalten werden.Activated(): Diese Methode wird jedes Mal aufgerufen, wenn der Benutzer zu diesem Arbeitsbereich wechselt. Sie eignet sich, um kontextspezifische UI-Elemente zu laden, Beobachter (Observer) zu registrieren oder andere ressourcenintensivere Initialisierungen durchzuführen.Deactivated(): Diese Methode wird jedes Mal aufgerufen, wenn der Benutzer von diesem Arbeitsbereich zu einem anderen wechselt. Sie dient dem Aufräumen, z. B. dem Entfernen von Beobachtern oder UI-Elementen, die in anderen Arbeitsbereichen nicht vorhanden sein sollen.Diese "Just-in-Time"-Architektur, bei der ressourcenintensive Operationen auf die Activated()-Methode verschoben werden, ist ein Schlüsselkonzept für die Entwicklung performanter Addons. FreeCAD lädt beim Start Informationen über alle verfügbaren Module, um die Workbench-Liste zu füllen. Würde jedes Addon in seiner Initialize()-Methode schwere Aufgaben ausführen, würde sich die Startzeit der Anwendung drastisch verlängern. Die Lebenszyklus-Methoden ermöglichen ein effizientes "Lazy Loading".Registrierung der WorkbenchNachdem die Klasse vollständig definiert wurde, muss eine Instanz davon erstellt und explizit bei der FreeCAD-GUI registriert werden. Ohne diesen letzten Schritt würde FreeCAD die neue Workbench nicht erkennen.5Python# Am Ende der InitGui.py Datei
FreeCADGui.addWorkbench(ProtoWorkbench())
Ein umfassender Leitfaden zur Iconographie von WorkbenchesDie visuelle Darstellung einer Workbench durch ein Icon ist entscheidend für die Benutzererfahrung und die Wiedererkennung. Dieser Abschnitt widmet sich vollständig der korrekten Implementierung von Icons.Prinzipien des Icon-Designs und FormatFür eine nahtlose Integration in die FreeCAD-Oberfläche sollten Icons bestimmten Konventionen folgen:Format: Das bevorzugte Format ist SVG (Scalable Vector Graphics), da es verlustfrei skaliert und sich an verschiedene UI-Themes (hell/dunkel) anpassen lässt.15Größe: Die nominale Größe für Icons ist 64x64 Pixel.16Stil: Es wird empfohlen, ein klares, einfaches Design zu wählen, das auch bei kleiner Skalierung erkennbar bleibt und stilistisch zu den Standard-Icons von FreeCAD passt.Methode 1: Verknüpfung mit einer externen Icon-Datei (Empfohlen)Dies ist die modernste und flexibelste Methode. Sie hält Code und grafische Assets getrennt, was die Wartung und Bearbeitung der Icons erheblich vereinfacht. Der Icon-Attribut der Workbench-Klasse wird auf den Pfad zur SVG-Datei gesetzt.Eine häufige Fehlerquelle ist die Verwendung von fest kodierten (absoluten) Pfaden. Da ein Addon an verschiedenen Orten installiert sein kann (systemweit oder benutzerspezifisch) 8, muss der Pfad zur Icon-Datei zur Laufzeit dynamisch ermittelt werden. Dies geschieht am besten mithilfe des **file**-Attributs von Python, das den Pfad des aktuellen Skripts (InitGui.py) enthält.Pythonimport os

#... innerhalb der InitGui.py...

# Dynamische Ermittlung des Icon-Pfades

icon_path = os.path.join(os.path.dirname(**file**), "icons", "ProtoWB.svg")

class ProtoWorkbench(Workbench):
MenuText = "ProtoWB"
ToolTip = "Ein Prototyp einer Workbench."
Icon = icon*path
#...
Methode 2: Einbetten von XPM-Icon-Daten (Veraltet)Eine ältere Methode besteht darin, die Bilddaten direkt als mehrzeilige Zeichenkette im XPM-Format in die InitGui.py-Datei einzubetten.5Pythonclass MyWorkbench(Workbench):
MenuText = "My Workbench"
ToolTip = "A description of my workbench"
Icon = """
/* XPM _/
static char _ my*icon_xpm = {
"16 16 2 1",
" c None",
". c #000000",
"................",
"................",
"/*... weitere XPM-Daten... \*/"
};
"""
#...
Diese Methode wird für neue Projekte nicht empfohlen. Das XPM-Format ist veraltet, schwer zu erstellen und zu bearbeiten, und die eingebetteten Daten machen den Python-Code unübersichtlich und schwer lesbar.Methode 3: Verwendung des Qt-Ressourcensystems (Fortgeschritten)Dies ist die professionellste und performanteste Methode, die vor allem bei komplexen Addons zum Einsatz kommt. Alle Assets (Icons, UI-Dateien etc.) werden mithilfe des Qt-Ressourcen-Compilers (pyside-rcc) in eine einzige Python-Datei kompiliert.5Der Prozess umfasst folgende Schritte:Erstellen einer .qrc-Datei (eine XML-Datei), die alle Ressourcen auflistet.Ausführen des Tools pyside-rcc, um aus der .qrc-Datei eine resources.py-Datei zu generieren.Importieren der generierten resources.py in InitGui.py.Referenzieren der Icons über einen speziellen Ressourcenpfad (z. B. :/icons/ProtoWB.svg).Diese Methode eliminiert externe Dateiabhängigkeiten und verbessert die Ladezeiten, da kein direkter Festplattenzugriff mehr für das Laden der Icons erforderlich ist. Sie führt jedoch einen zusätzlichen Build-Schritt in den Entwicklungsprozess ein.Die folgende Tabelle vergleicht die drei Methoden und hilft bei der Auswahl des richtigen Ansatzes.MethodeVorteileNachteileBeste EignungExterne SVG-VerknüpfungEinfache Erstellung/Bearbeitung der Icons. Gute Trennung von Code und Assets. Modernes Format.Erfordert sorgfältiges Pfadmanagement. Geringfügig langsamer (Festplatten-I/O).Empfohlen für die meisten Addons. Einfach, flexibel und leicht zu warten.Eingebettetes XPMVollständig autarkes Skript. Keine externen Dateien.Sehr schwierige Erstellung/Bearbeitung der Icons. Bläht die Quellcodedatei auf. Veraltetes Format.Veraltete Addons oder extrem einfache Ein-Datei-Makro-Tools. Nicht für neue Workbenches empfohlen.Qt-Ressourcensystem (.qrc)Höchste Performance. Alle Assets in eine Datei kompiliert. Keine externen Abhängigkeiten. Professionellster Ansatz.Fügt dem Entwicklungsprozess einen Build-Schritt hinzu. Komplexere Einrichtung.Komplexe Addons, kommerzielle Addons oder Projekte, bei denen Performance und professionelle Verteilung im Vordergrund stehen.Eine vollständige Implementierung: Erstellung von "ProtoWB" von Grund aufDieser Abschnitt führt den Benutzer durch die Erstellung der Beispiel-Workbench "ProtoWB" und wendet dabei alle zuvor besprochenen Prinzipien an. Dies ist ein vollständiges, funktionierendes Beispiel.Schritt 1: Erstellen der VerzeichnisstrukturErstellen Sie die folgende Ordner- und Dateistruktur innerhalb Ihres FreeCAD Mod-Verzeichnisses:Mod/
└── ProtoWB/
├── Init.py
├── InitGui.py
├── ProtoWB/
│ └── **init**.py
│ └── commands.py
└── icons/
├── ProtoWB.svg
└── ProtoWB_Command1.svg
Die Datei ProtoWB/**init**.py kann leer bleiben; sie dient dazu, das Verzeichnis als Python-Paket zu kennzeichnen.Schritt 2: Entwerfen der IconsErstellen Sie zwei einfache SVG-Dateien. Für ProtoWB.svg und ProtoWB_Command1.svg können Sie einen Vektorgrafik-Editor wie Inkscape verwenden. Speichern Sie diese im icons/-Verzeichnis.Schritt 3: Schreiben von Init.pyDiese Datei ist für unser einfaches Beispiel leer, muss aber existieren.Mod/ProtoWB/Init.py:Python# Diese Datei wird von FreeCAD benötigt, um das Modul zu erkennen.

# Sie kann für nicht-GUI-Initialisierungen verwendet werden.

# Für unser Beispiel bleibt sie leer.

pass
Schritt 4: Hinzufügen eines einfachen BefehlsEin Befehl (Command) ist eine Aktion, die der Benutzer ausführen kann, z. B. durch Klicken auf eine Schaltfläche in einer Werkzeugleiste. Jeder Befehl wird durch eine eigene Python-Klasse definiert.12Mod/ProtoWB/ProtoWB/commands.py:Pythonimport FreeCAD
import FreeCADGui

class ProtoCommand1:
"""Ein einfacher Beispiel-Befehl."""

    def Activated(self):
        """Diese Methode wird ausgeführt, wenn der Befehl aktiviert wird."""
        FreeCAD.Console.PrintMessage("ProtoCommand1 wurde ausgeführt!\n")

    def GetResources(self):
        """
        Diese Methode gibt die Ressourcen für den Befehl zurück.
        'Pixmap': Der Pfad zum Icon des Befehls (16x16 oder 32x32 Pixel).
        'MenuText': Der Text, der im Menü erscheint.
        'ToolTip': Der Text, der als Tooltip angezeigt wird.
        """
        # Wir importieren 'os' hier, um den Pfad dynamisch zu erstellen
        import os
        # __file__ verweist auf den Speicherort dieser Datei (commands.py)
        # Wir navigieren von hier zum 'icons'-Verzeichnis
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "ProtoWB_Command1.svg")

        return {
            'Pixmap': icon_path,
            'MenuText': 'Proto Command 1',
            'ToolTip': 'Führt den ersten Prototyp-Befehl aus.'
        }

# Registrieren des Befehls bei FreeCAD

FreeCADGui.addCommand('ProtoCommand1', ProtoCommand1())
Schritt 5: Schreiben des InitGui.py-SkriptsDies ist das Hauptskript, das die Workbench, ihre Werkzeugleiste und ihr Icon definiert.Mod/ProtoWB/InitGui.py:Pythonimport FreeCADGui
import os

class ProtoWorkbench(FreeCADGui.Workbench):
"""
Die Definition unserer Prototyp-Workbench.
"""

    # Der Name, der im Workbench-Auswahlmenü angezeigt wird.
    MenuText = "ProtoWB"

    # Der Tooltip, der angezeigt wird, wenn man mit der Maus darüber fährt.
    ToolTip = "Ein Prototyp einer Workbench zur Demonstration."

    def GetClassName(self):
        # Dies muss der Name der C++-Basisklasse oder der Python-Klasse sein.
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        Diese Methode wird einmal aufgerufen, wenn die Workbench initialisiert wird.
        """
        # Importieren der Befehlsklasse. Der Import hier stellt sicher,
        # dass der Code nur geladen wird, wenn die Workbench benötigt wird.
        from.ProtoWB import commands

        # Erstellen einer Liste von Befehlsnamen, die zur Werkzeugleiste hinzugefügt werden sollen.
        # Der Name muss mit dem bei addCommand registrierten Namen übereinstimmen.
        command_list = ["ProtoCommand1"]

        # Hinzufügen einer Werkzeugleiste zur Workbench.
        self.appendToolbar("ProtoWB Commands", command_list)

        FreeCAD.Console.PrintMessage("ProtoWB initialisiert.\n")

    def Activated(self):
        """Wird aufgerufen, wenn die Workbench aktiviert wird."""
        FreeCAD.Console.PrintMessage("ProtoWB aktiviert.\n")

    def Deactivated(self):
        """Wird aufgerufen, wenn die Workbench deaktiviert wird."""
        FreeCAD.Console.PrintMessage("ProtoWB deaktiviert.\n")

# Dynamische Ermittlung des Pfades zum Workbench-Icon.

# os.path.dirname(**file**) gibt das Verzeichnis dieser Datei (InitGui.py) zurück.

icon_path = os.path.join(os.path.dirname(**file**), "icons", "ProtoWB.svg")

# Zuweisen des Icon-Pfades zur Icon-Eigenschaft der Klasse.

ProtoWorkbench.Icon = icon_path

# Registrieren der Workbench bei der FreeCAD-GUI.

FreeCADGui.addWorkbench(ProtoWorkbench())
Schritt 6: Installation und TestKopieren Sie das gesamte ProtoWB-Verzeichnis in Ihren FreeCAD Mod-Ordner. Den genauen Pfad finden Sie, wie in Abschnitt 1.3 beschrieben, über die Python-Konsole.8Starten Sie FreeCAD neu.Öffnen Sie das Workbench-Auswahlmenü. Sie sollten nun einen neuen Eintrag "ProtoWB" mit dem von Ihnen erstellten Icon sehen.Wählen Sie die "ProtoWB"-Workbench aus. Eine neue Werkzeugleiste mit dem Namen "ProtoWB Commands" und einer Schaltfläche sollte erscheinen.Klicken Sie auf die Schaltfläche. In der Python-Konsole (Ansicht -> Paneele -> Python-Konsole) sollte die Nachricht "ProtoCommand1 wurde ausgeführt!" erscheinen.Professionelle Entwicklungspraktiken und fortgeschrittene TechnikenDie Erstellung einer funktionierenden Workbench ist der erste Schritt. Für die Entwicklung hochwertiger, wartbarer und benutzerfreundlicher Addons sollten fortgeschrittene Techniken und Best Practices berücksichtigt werden.Bootstrapping von Projekten mit Starter-KitsUm den Einrichtungsprozess zu beschleunigen und sicherzustellen, dass von Anfang an Best Practices befolgt werden, stellt das FreeCAD-Projekt ein offizielles Starter-Kit zur Verfügung: freecad.workbench_starterkit. Dieses Kit verwendet das Werkzeug cookiecutter, um automatisch eine vollständige, kanonische Projektstruktur basierend auf einer Vorlage zu generieren.4 Dies automatisiert die Erstellung der Verzeichnisstruktur und des Boilerplate-Codes, der in diesem Bericht beschrieben wurde, und ist der empfohlene Weg, um ein neues Workbench-Projekt zu beginnen.Erstellung von Benutzeroberflächen mit Qt DesignerFür komplexere Benutzeroberflächen, wie z. B. Dialoge oder die "Task Panel", ist das manuelle Schreiben von UI-Code in Python mühsam und fehleranfällig. Die empfohlene Methode ist die Verwendung von Qt Designer, einem visuellen UI-Editor. Mit diesem Werkzeug können Oberflächen per Drag-and-Drop entworfen und als .ui-Dateien gespeichert werden. Diese .ui-Dateien können dann zur Laufzeit dynamisch in FreeCAD geladen und mit der Anwendungslogik verknüpft werden.2 Dieser Ansatz fördert die Trennung von Design und Logik und vereinfacht die UI-Entwicklung erheblich.Die Bedeutung eines qualitativ hochwertigen AddonsDie Veröffentlichung eines Addons bedeutet, Teil des FreeCAD-Ökosystems zu werden. Die Qualität eines Addons hat einen direkten Einfluss auf die Benutzererfahrung und die Wahrnehmung des gesamten FreeCAD-Projekts. Die FreeCAD-Community und die Kernentwickler legen zunehmend Wert auf die Qualität von Addons.2 Wichtige Qualitätsmerkmale umfassen:Übersetzbarkeit: Alle für den Benutzer sichtbaren Zeichenketten sollten für die Übersetzung vorbereitet werden, um das Addon einem internationalen Publikum zugänglich zu machen.2Parametrische Objekte: Neu erstellte Objekte sollten parametrisch sein, d. h., ihre Eigenschaften sollten über das Eigenschaften-Panel modifizierbar bleiben.2Unit-Tests: Das Schreiben von automatisierten Tests hilft, die Stabilität des Addons zu gewährleisten und Regressionen bei zukünftigen Änderungen zu vermeiden.2Einhaltung von UI/UX-Richtlinien: Addons sollten sich nahtlos in die bestehende FreeCAD-Oberfläche einfügen und etablierten Designmustern folgen.23Die Existenz des Addon Managers 7, umfangreicher Addon-Repositories 24 und von Entwicklerhandbüchern 23 zeigt ein reifes und aktives Ökosystem. Ein Entwickler veröffentlicht nicht nur Code, sondern trägt zu diesem gemeinsamen System bei. Der langfristige Erfolg und die Akzeptanz eines Addons hängen nicht nur von seiner Funktionalität ab, sondern auch von seiner Einhaltung dieser gemeinschaftlichen Qualitätsstandards.SchlussfolgerungDie Erstellung eines FreeCAD-Addons ist ein zugänglicher Prozess, der jedoch ein grundlegendes Verständnis der Kernarchitektur von FreeCAD erfordert. Die strikte Trennung von Anwendungs- und GUI-Logik, die sich in der Verwendung von Init.py und InitGui.py widerspiegelt, ist das Fundament für stabile und vielseitige Erweiterungen.Die Initialisierung einer Workbench und die Zuweisung ihres Icons erfolgen primär in der InitGui.py-Datei durch die Definition einer Workbench-Klasse mit spezifischen Attributen wie MenuText, ToolTip und Icon. Die empfohlene Methode zur Icon-Zuweisung ist die dynamische Verknüpfung zu einer externen SVG-Datei, da sie Flexibilität und Wartbarkeit maximiert.Das in diesem Bericht vorgestellte vollständige Beispiel "ProtoWB" demonstriert diese Kernkonzepte in der Praxis und bietet eine solide Grundlage, auf der Entwickler aufbauen können. Durch die Anwendung professioneller Entwicklungspraktiken, wie die Verwendung von Starter-Kits, Qt Designer und die Einhaltung von Qualitätsstandards, können Entwickler hochwertige Addons erstellen, die eine wertvolle Bereicherung für die gesamte FreeCAD-Community darstellen.
