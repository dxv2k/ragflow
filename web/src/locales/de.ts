export default {
  translation: {
    common: {
      delete: 'Löschen',
      deleteModalTitle:
        'Sind Sie sicher, dass Sie diesen Eintrag löschen möchten?',
      ok: 'Ja',
      cancel: 'Nein',
      total: 'Gesamt',
      rename: 'Umbenennen',
      name: 'Name',
      save: 'Speichern',
      namePlaceholder: 'Bitte Namen eingeben',
      next: 'Weiter',
      create: 'Erstellen',
      edit: 'Bearbeiten',
      upload: 'Hochladen',
      english: 'Englisch',
      portugueseBr: 'Portugiesisch (Brasilien)',
      chinese: 'Vereinfachtes Chinesisch',
      traditionalChinese: 'Traditionelles Chinesisch',
      german: 'Deutsch',
      language: 'Sprache',
      languageMessage: 'Bitte geben Sie Ihre Sprache ein!',
      languagePlaceholder: 'Wählen Sie Ihre Sprache',
      copy: 'Kopieren',
      copied: 'Kopiert',
      comingSoon: 'Demnächst verfügbar',
      download: 'Herunterladen',
      close: 'Schließen',
      preview: 'Vorschau',
      move: 'Verschieben',
      warn: 'Warnung',
      action: 'Aktion',
      s: 'S',
      pleaseSelect: 'Bitte auswählen',
      pleaseInput: 'Bitte eingeben',
      submit: 'Absenden',
      embedIntoSite: 'In Webseite einbetten',
      previousPage: 'Zurück',
      nextPage: 'Weiter',
    },
    login: {
      login: 'Anmelden',
      signUp: 'Registrieren',
      loginDescription: 'Wir freuen uns, Sie wiederzusehen!',
      registerDescription: 'Schön, Sie an Bord zu haben!',
      emailLabel: 'E-Mail',
      emailPlaceholder: 'Bitte E-Mail eingeben',
      passwordLabel: 'Passwort',
      passwordPlaceholder: 'Bitte Passwort eingeben',
      rememberMe: 'Angemeldet bleiben',
      signInTip: 'Noch kein Konto?',
      signUpTip: 'Bereits ein Konto?',
      nicknameLabel: 'Spitzname',
      nicknamePlaceholder: 'Bitte Spitznamen eingeben',
      register: 'Konto erstellen',
      continue: 'Fortfahren',
      title: 'Beginnen Sie mit dem Aufbau Ihrer intelligenten Assistenten.',
      description:
        'Registrieren Sie sich kostenlos, um führende RAG-Technologie zu erkunden. Erstellen Sie Wissensdatenbanken und KIs, um Ihr Unternehmen zu stärken.',
      review: 'von über 500 Bewertungen',
    },
    header: {
      knowledgeBase: 'Wissensdatenbank',
      chat: 'Chat',
      register: 'Registrieren',
      signin: 'Anmelden',
      home: 'Startseite',
      setting: 'Benutzereinstellungen',
      logout: 'Abmelden',
      fileManager: 'Dateiverwaltung',
      flow: 'Agent',
      search: 'Suche',
    },
    knowledgeList: {
      welcome: 'Willkommen zurück',
      description: 'Welche Wissensdatenbanken möchten Sie heute nutzen?',
      createKnowledgeBase: 'Wissensdatenbank erstellen',
      name: 'Name',
      namePlaceholder: 'Bitte Namen eingeben!',
      doc: 'Dokumente',
      searchKnowledgePlaceholder: 'Suchen',
      noMoreData: `Das war's. Nichts mehr zu sehen.`,
    },
    knowledgeDetails: {
      dataset: 'Datensatz',
      testing: 'Abruftest',
      files: 'Dateien',
      configuration: 'Konfiguration',
      knowledgeGraph: 'Wissensgraph',
      name: 'Name',
      namePlaceholder: 'Bitte Namen eingeben!',
      doc: 'Dokumente',
      datasetDescription:
        '😉 Bitte warten Sie, bis die Analyse Ihrer Datei abgeschlossen ist, bevor Sie einen KI-gestützten Chat starten.',
      addFile: 'Datei hinzufügen',
      searchFiles: 'Durchsuchen Sie Ihre Dateien',
      localFiles: 'Lokale Dateien',
      emptyFiles: 'Leere Datei erstellen',
      webCrawl: 'Web-Crawling',
      chunkNumber: 'Chunk-Anzahl',
      uploadDate: 'Hochladedatum',
      chunkMethod: 'Chunk-Methode',
      enabled: 'Aktiviert',
      disabled: 'Deaktiviert',
      action: 'Aktion',
      parsingStatus: 'Analysestatus',
      parsingStatusTip:
        'Die Verarbeitungszeit für Dokumente variiert je nach mehreren Faktoren. Das Aktivieren von Funktionen wie Knowledge Graph, RAPTOR, automatischer Frage- oder Schlüsselwort-Extraktion verlängert die Bearbeitungszeit deutlich. Wenn der Fortschrittsbalken stehen bleibt, konsultieren Sie bitte diese beiden FAQs: https://ragflow.io/docs/dev/faq#why-does-my-document-parsing-stall-at-under-one-percent.',
      processBeginAt: 'Beginn',
      processDuration: 'Dauer',
      progressMsg: 'Fortschritt',
      testingDescription:
        'Führen Sie einen Abruftest durch, um zu prüfen, ob RAGFlow die beabsichtigten Inhalte für das LLM wiederherstellen kann.',
      similarityThreshold: 'Ähnlichkeitsschwelle',
      similarityThresholdTip:
        'RAGFlow verwendet entweder eine Kombination aus gewichteter Schlüsselwortähnlichkeit und gewichteter Vektorkosinus-Ähnlichkeit oder eine Kombination aus gewichteter Schlüsselwortähnlichkeit und gewichteter Neuordnungsbewertung während des Abrufs. Dieser Parameter legt den Schwellenwert für Ähnlichkeiten zwischen der Benutzeranfrage und den Chunks fest. Jeder Chunk mit einer Ähnlichkeitsbewertung unter diesem Schwellenwert wird von den Ergebnissen ausgeschlossen. Standardmäßig ist der Schwellenwert auf 0,2 festgelegt. Das bedeutet, dass nur Textblöcke mit einer hybriden Ähnlichkeitsbewertung von 20 oder höher abgerufen werden.',
      vectorSimilarityWeight: 'Schlüsselwortähnlichkeitsgewicht',
      vectorSimilarityWeightTip:
        'Dies legt das Gewicht der Schlüsselwortähnlichkeit im kombinierten Ähnlichkeitswert fest, entweder in Verbindung mit der Vektorkosinus-Ähnlichkeit oder mit der Neuordnungsbewertung. Die Summe der beiden Gewichte muss 1,0 ergeben.',
      testText: 'Testtext',
      testTextPlaceholder: 'Geben Sie hier Ihre Frage ein!',
      testingLabel: 'Testen',
      similarity: 'Hybride Ähnlichkeit',
      termSimilarity: 'Begriffsähnlichkeit',
      vectorSimilarity: 'Vektorähnlichkeit',
      hits: 'Treffer',
      view: 'Ansehen',
      filesSelected: 'Dateien ausgewählt',
      upload: 'Hochladen',
      run: 'Analysieren',
      runningStatus0: 'AUSSTEHEND',
      runningStatus1: 'WIRD ANALYSIERT',
      runningStatus2: 'ABGEBROCHEN',
      runningStatus3: 'ERFOLGREICH',
      runningStatus4: 'FEHLGESCHLAGEN',
      pageRanges: 'Seitenbereiche',
      pageRangesTip:
        'Bereich der zu analysierenden Seiten; Seiten außerhalb dieses Bereichs werden nicht verarbeitet.',
      fromPlaceholder: 'von',
      fromMessage: 'Anfangsseitennummer fehlt',
      toPlaceholder: 'bis',
      toMessage: 'Endseitennummer fehlt (ausgeschlossen)',
      layoutRecognize: 'Dokumentenparser',
      layoutRecognizeTip:
        'Verwendet ein visuelles Modell für die PDF-Layout-Analyse, um Dokumententitel, Textblöcke, Bilder und Tabellen effektiv zu lokalisieren. Wenn die einfache Option gewählt wird, wird nur der reine Text im PDF abgerufen. Bitte beachten Sie, dass diese Option derzeit NUR für PDF-Dokumente funktioniert.',
      taskPageSize: 'Aufgabenseitengröße',
      taskPageSizeMessage: 'Bitte geben Sie die Größe der Aufgabenseite ein!',
      taskPageSizeTip:
        'Während der Layouterkennung wird eine PDF-Datei in Chunks aufgeteilt und parallel verarbeitet, um die Verarbeitungsgeschwindigkeit zu erhöhen. Dieser Parameter legt die Größe jedes Chunks fest. Eine größere Chunk-Größe verringert die Wahrscheinlichkeit, dass fortlaufender Text zwischen den Seiten aufgeteilt wird.',
      addPage: 'Seite hinzufügen',
      greaterThan: 'Der aktuelle Wert muss größer als "bis" sein!',
      greaterThanPrevious:
        'Der aktuelle Wert muss größer als der vorherige "bis"-Wert sein!',
      selectFiles: 'Dateien auswählen',
      changeSpecificCategory: 'Spezifische Kategorie ändern',
      uploadTitle: 'Ziehen Sie Ihre Datei hierher, um sie hochzuladen',
      uploadDescription:
        'RAGFlow unterstützt das Hochladen von Dateien einzeln oder in Batches. Für lokal bereitgestelltes RAGFlow: Die maximale Dateigröße pro Upload beträgt 1 GB, mit einem Batch-Upload-Limit von 32 Dateien. Es gibt keine Begrenzung der Gesamtanzahl an Dateien pro Konto. Für demo.ragflow.io: Die maximale Dateigröße pro Upload beträgt 10 MB, wobei jede Datei nicht größer als 10 MB sein darf und maximal 128 Dateien pro Konto erlaubt sind.',
      chunk: 'Chunk',
      bulk: 'Masse',
      cancel: 'Abbrechen',
      rerankModel: 'Neuordnungsmodell',
      rerankPlaceholder: 'Bitte auswählen',
      rerankTip:
        'Wenn leer gelassen, verwendet RAGFlow eine Kombination aus gewichteter Schlüsselwortähnlichkeit und gewichteter Vektorkosinus-Ähnlichkeit; wenn ein Neuordnungsmodell ausgewählt wird, ersetzt eine gewichtete Neuordnungsbewertung die gewichtete Vektorkosinus-Ähnlichkeit. Bitte beachten Sie, dass die Verwendung eines Neuordnungsmodells die Antwortzeit des Systems erheblich erhöht.',
      topK: 'Top-K',
      topKTip:
        'In Verbindung mit dem Rerank model wird mit dieser Einstellung die Anzahl der Textblöcke festgelegt, die an das angegebene reranking model gesendet werden.',
      delimiter: 'Trennzeichen für Textsegmentierung',
      delimiterTip:
        'Ein Trennzeichen oder Separator kann aus einem oder mehreren Sonderzeichen bestehen. Bei mehreren Zeichen stellen Sie sicher, dass sie in Backticks (` `) eingeschlossen sind. Wenn Sie beispielsweise Ihre Trennzeichen so konfigurieren: \\n`##`;, dann werden Ihre Texte an Zeilenumbrüchen, doppelten Rautenzeichen (##) oder Semikolons getrennt. Setzen Sie Trennzeichen nur nachdem Sie das Mechanismus der Textsegmentierung und -chunking verstanden haben.',
      html4excel: 'Excel zu HTML',
      html4excelTip:
        'Verwenden Sie dies zusammen mit der General-Schnittmethode. Wenn deaktiviert, werden Tabellenkalkulationsdateien (XLSX, XLS (Excel 97-2003)) zeilenweise in Schlüssel-Wert-Paare analysiert. Wenn aktiviert, werden Tabellenkalkulationsdateien in HTML-Tabellen umgewandelt. Wenn die ursprüngliche Tabelle mehr als 12 Zeilen enthält, teilt das System sie automatisch alle 12 Zeilen in mehrere HTML-Tabellen auf. Für weitere Informationen siehe https://ragflow.io/docs/dev/enable_excel2html.',
      autoKeywords: 'Auto-Schlüsselwort',
      autoKeywordsTip:
        'Extrahieren Sie automatisch N Schlüsselwörter für jeden Abschnitt, um deren Ranking in Abfragen mit diesen Schlüsselwörtern zu verbessern. Beachten Sie, dass zusätzliche Tokens vom in den "Systemmodelleinstellungen" angegebenen Chat-Modell verbraucht werden. Sie können die hinzugefügten Schlüsselwörter eines Abschnitts in der Abschnittsliste überprüfen oder aktualisieren.',
      autoQuestions: 'Auto-Frage',
      autoQuestionsTip:
        'Um die Ranking-Ergebnisse zu verbessern, extrahieren Sie N Fragen für jeden Wissensdatenbank-Chunk mithilfe des im "Systemmodell-Setup" definierten Chatmodells. Beachten Sie, dass dies zusätzliche Token verbraucht. Die Ergebnisse können in der Chunk-Liste eingesehen und bearbeitet werden. Fehler bei der Fragenextraktion blockieren den Chunking-Prozess nicht; leere Ergebnisse werden dem ursprünglichen Chunk hinzugefügt.',
      redo: 'Möchten Sie die vorhandenen {{chunkNum}} Chunks löschen?',
      setMetaData: 'Metadaten festlegen',
      pleaseInputJson: 'Bitte JSON eingeben',
      documentMetaTips: `<p>Die Metadaten liegen im JSON-Format vor (nicht durchsuchbar). Sie werden dem Prompt für das LLM hinzugefügt, wenn Chunks dieses Dokuments im Prompt enthalten sind.</p>
  <p>Beispiele:</p>
  <b>Die Metadaten sind:</b><br>
  <code>
    {
        "Author": "Alex Dowson",
        "Date": "2024-11-12"
    }
  </code><br>
  <b>Der Prompt wird sein:</b><br>
  <p>Dokument: the_name_of_document</p>
  <p>Autor: Alex Dowson</p>
  <p>Datum: 2024-11-12</p>
  <p>Relevante Fragmente wie folgt:</p>
  <ul>
  <li>  Hier ist der Chunk-Inhalt....</li>
  <li>  Hier ist der Chunk-Inhalt....</li>
  </ul>
  `,
      metaData: 'Metadaten',
      deleteDocumentConfirmContent:
        'Das Dokument ist mit dem Wissensgraphen verknüpft. Nach dem Löschen werden die zugehörigen Knoten- und Beziehungsinformationen gelöscht, aber der Graph wird nicht sofort aktualisiert. Die Aktualisierung des Graphen erfolgt während des Analyseprozesses des neuen Dokuments, das die Aufgabe zur Extraktion des Wissensgraphen enthält.',
      plainText: 'Einfach',
    },
    knowledgeConfiguration: {
      titleDescription:
        'Aktualisieren Sie hier Ihre Wissensdatenbank-Konfiguration, insbesondere die Chunk-Methode.',
      name: 'Name der Wissensdatenbank',
      photo: 'Bild der Wissensdatenbank',
      description: 'Beschreibung',
      language: 'Dokumentensprache',
      languageMessage: 'Bitte geben Sie Ihre Sprache ein!',
      languagePlaceholder: 'Bitte geben Sie Ihre Sprache ein!',
      permissions: 'Berechtigungen',
      embeddingModel: 'Embedding-Modell',
      chunkTokenNumber: 'Empfohlene Chunk-Größe',
      chunkTokenNumberMessage: 'Chunk-Token-Anzahl ist erforderlich',
      embeddingModelTip:
        'Das Standard-Embedding-Modell der Wissensdatenbank. Es kann nicht geändert werden, sobald die Wissensdatenbank Chunks enthält. Um zu einem anderen Standard-Embedding-Modell zu wechseln, müssen alle vorhandenen Chunks in der Wissensdatenbank gelöscht werden.',
      permissionsTip:
        'Wenn auf "Team" gesetzt, können alle Teammitglieder die Wissensdatenbank verwalten.',
      chunkTokenNumberTip:
        'Legt den Token-Schwellenwert für einen Chunk fest. Ein Absatz mit weniger Tokens als dieser Schwellenwert wird mit dem folgenden Absatz kombiniert, bis die Token-Anzahl den Schwellenwert überschreitet, dann wird ein Chunk erstellt. Ein neuer Block wird nicht erstellt, es sei denn, ein Trennzeichen wird gefunden, auch wenn dieser Schwellenwert überschritten wird.',
      chunkMethod: 'Chunk-Methode',
      chunkMethodTip: 'Siehe Tipps auf der rechten Seite.',
      upload: 'Hochladen',
      english: 'Englisch',
      chinese: 'Chinesisch',
      portugueseBr: 'Portugiesisch (Brasilien)',
      embeddingModelPlaceholder: 'Bitte wählen Sie ein Embedding-Modell',
      chunkMethodPlaceholder: 'Bitte wählen Sie eine Chunk-Methode',
      save: 'Speichern',
      me: 'Nur ich',
      team: 'Team',
      cancel: 'Abbrechen',
      methodTitle: 'Beschreibung der Chunk-Methode',
      methodExamples: 'Beispiele',
      methodExamplesDescription:
        'Die folgenden Screenshots dienen zur Verdeutlichung.',
      dialogueExamplesTitle: 'Dialogbeispiele',
      methodEmpty:
        'Hier wird eine visuelle Erklärung der Wissensdatenbank-Kategorien angezeigt',
      book: `<p>Unterstützte Dateiformate sind <b>DOCX</b>, <b>PDF</b>, <b>TXT</b>.</p><p>
        Für jedes Buch im PDF-Format stellen Sie bitte die <i>Seitenbereiche</i> ein, um unerwünschte Informationen zu entfernen und die Analysezeit zu reduzieren.</p>`,
      laws: `<p>Unterstützte Dateiformate sind <b>DOCX</b>, <b>PDF</b>, <b>TXT</b>.</p><p>
        Rechtliche Dokumente folgen in der Regel einem strengen Schreibformat. Wir verwenden Textmerkmale, um Teilungspunkte zu identifizieren.
        </p><p>
        Der Chunk hat eine Granularität, die mit 'ARTIKEL' übereinstimmt, wobei sichergestellt wird, dass der gesamte übergeordnete Text im Chunk enthalten ist.
        </p>`,
      manual: `<p>Nur <b>PDF</b> wird unterstützt.</p><p>
        Wir gehen davon aus, dass das Handbuch eine hierarchische Abschnittsstruktur aufweist und verwenden die Titel der untersten Abschnitte als Grundeinheit für die Aufteilung der Dokumente. Daher werden Abbildungen und Tabellen im selben Abschnitt nicht getrennt, was zu größeren Chunk-Größen führen kann.
        </p>`,
      naive: `<p>Unterstützte Dateiformate sind <b>DOCX, XLSX, XLS (Excel 97-2003), PPT, PDF, TXT, JPEG, JPG, PNG, TIF, GIF, CSV, JSON, EML, HTML</b>.</p>
        <p>Diese Methode teilt Dateien mit einer 'naiven' Methode auf: </p>
        <p>
        <li>Verwenden eines Erkennungsmodells, um die Texte in kleinere Segmente aufzuteilen.</li>
        <li>Dann werden benachbarte Segmente kombiniert, bis die Token-Anzahl den durch 'Chunk-Token-Anzahl' festgelegten Schwellenwert überschreitet, woraufhin ein Chunk erstellt wird.</li></p>`,
      paper: `<p>Nur <b>PDF</b>-Dateien werden unterstützt.</p><p>
        Papers werden nach Abschnitten wie <i>abstract, 1.1, 1.2</i> aufgeteilt. </p><p>
        Dieser Ansatz ermöglicht es dem LLM, das Paper effektiver zusammenzufassen und umfassendere, verständlichere Antworten zu liefern.
        Es erhöht jedoch auch den Kontext für KI-Gespräche und die Rechenkosten für das LLM. Daher sollten Sie während eines Gesprächs erwägen, den Wert von '<b>topN</b>' zu reduzieren.</p>`,
      presentation: `<p>Unterstützte Dateiformate sind <b>PDF</b>, <b>PPTX</b>.</p><p>
        Jede Seite in den Folien wird als Chunk behandelt, wobei ihr Vorschaubild gespeichert wird.</p><p>
        <i>Diese Chunk-Methode wird automatisch auf alle hochgeladenen PPT-Dateien angewendet, Sie müssen sie also nicht manuell angeben.</i></p>`,
      qa: `
        <p>
        Diese Chunk-Methode unterstützt die Dateiformate <b>XLSX</b> und <b>CSV/TXT</b>.
      </p>
      <li>
        Wenn eine Datei im <b>XLSX</b>-Format vorliegt, sollte sie zwei Spalten
        ohne Kopfzeilen enthalten: eine für Fragen und die andere für Antworten, wobei die
        Fragenspalte der Antwortspalte vorangeht. Mehrere Blätter sind
        akzeptabel, vorausgesetzt, die Spalten sind richtig strukturiert.
      </li>
      <li>
        Wenn eine Datei im <b>CSV/TXT</b>-Format vorliegt, muss sie UTF-8-kodiert sein und TAB als Trennzeichen verwenden, um Fragen und Antworten zu trennen.
      </li>
      <p>
        <i>
          Textzeilen, die nicht den obigen Regeln folgen, werden ignoriert, und
          jedes Frage-Antwort-Paar wird als eigenständiger Chunk betrachtet.
        </i>
      </p>
        `,
      resume: `<p>Unterstützte Dateiformate sind <b>DOCX</b>, <b>PDF</b>, <b>TXT</b>.
        </p><p>
        Lebensläufe verschiedener Formen werden analysiert und in strukturierte Daten organisiert, um die Kandidatensuche für Recruiter zu erleichtern.
        </p>
        `,
      table: `<p>Unterstützte Dateiformate sind <b>XLSX</b> und <b>CSV/TXT</b>.</p><p>
        Hier sind einige Voraussetzungen und Tipps:
        <ul>
      <li>Für CSV- oder TXT-Dateien muss das Trennzeichen zwischen den Spalten <em><b>TAB</b></em> sein.</li>
      <li>Die erste Zeile muss Spaltenüberschriften enthalten.</li>
      <li>Spaltenüberschriften müssen aussagekräftige Begriffe sein, um das Verständnis Ihres LLM zu unterstützen.
      Es ist gute Praxis, Synonyme durch einen Schrägstrich <i>'/'</i> zu trennen und Werte unter Verwendung von Klammern aufzuzählen, zum Beispiel: <i>'Gender/Sex (male, female)'</i>.<p>
      Hier sind einige Beispiele für Überschriften:<ol>
          <li>supplier/vendor<b>'TAB'</b>Color (Yellow, Blue, Brown)<b>'TAB'</b>Sex/Gender (male, female)<b>'TAB'</b>size (M, L, XL, XXL)</li>
          </ol>
          </p>
      </li>
      <li>Jede Zeile in der Tabelle wird als Chunk behandelt.</li>
      </ul>`,
      picture: `
      <p>Bilddateien werden unterstützt, Videounterstützung folgt in Kürze.</p><p>
      Diese Methode verwendet ein OCR-Modell, um Texte aus Bildern zu extrahieren.
      </p><p>
      Wenn der vom OCR-Modell extrahierte Text als unzureichend angesehen wird, wird ein bestimmtes visuelles LLM verwendet, um eine Beschreibung des Bildes zu liefern.
      </p>`,
      one: `
      <p>Unterstützte Dateiformate sind <b>DOCX, EXCEL, PDF, TXT</b>.
      </p><p>
      Diese Methode behandelt jedes Dokument in seiner Gesamtheit als einen Chunk.
      </p><p>
      Anwendbar, wenn Sie das LLM das gesamte Dokument zusammenfassen lassen möchten, vorausgesetzt, es kann mit dieser Kontextlänge umgehen.
      </p>`,
      knowledgeGraph: `<p>Unterstützte Dateiformate sind <b>DOCX, EXCEL, PPT, IMAGE, PDF, TXT, MD, JSON, EML</b>

  <p>Dieser Ansatz teilt Dateien mit der 'naiven'/'Allgemeinen' Methode auf. Er teilt ein Dokument in Segmente und kombiniert dann benachbarte Segmente, bis die Token-Anzahl den durch 'Chunk-Token-Anzahl' festgelegten Schwellenwert überschreitet, woraufhin ein Chunk erstellt wird.</p>
  <p>Die Chunks werden dann dem LLM zugeführt, um Entitäten und Beziehungen für einen Wissensgraphen und eine Mind Map zu extrahieren.</p>
  <p>Stellen Sie sicher, dass Sie die <b>Entitätstypen</b> festlegen.</p>`,
      tag: `<p>Eine Wissensdatenbank, die die 'Tag'-Chunk-Methode verwendet, fungiert als Tag-Set. Andere Wissensdatenbanken können es verwenden, um ihre eigenen Chunks zu taggen, und Abfragen an diese Wissensdatenbanken werden ebenfalls mit diesem Tag-Set getaggt.</p>
      <p>Die Wissensdatenbank, die 'Tag' als Chunk-Methode verwendet, ist <b>NICHT</b> an einem Retrieval-Augmented Generation (RAG)-Prozess beteiligt.</p>
      <p>Jeder Chunk in dieser Wissensdatenbank ist ein unabhängiges Beschreibungs-Tag-Paar.</p>
      <p>Zu den unterstützten Dateiformaten gehören <b>XLSX</b> und <b>CSV/TXT</b>:</p>
      <p>Wenn eine Datei im <b>XLSX</b>-Format vorliegt, sollte sie zwei Spalten ohne Überschriften enthalten: eine für Tag-Beschreibungen und die andere für Tag-Namen, wobei die Spalte "Beschreibung" vor der Spalte "Tag" steht. Mehrere Blätter sind zulässig, sofern die Spalten ordnungsgemäß strukturiert sind.</p>
      <p>Wenn eine Datei im <b>CSV/TXT</b>-Format vorliegt, muss sie UTF-8-kodiert sein, wobei TAB als Trennzeichen zum Trennen von Beschreibungen und Tags verwendet wird.</p>
      <p>In einer Tag-Spalte wird das <b>Komma</b> verwendet, um Tags zu trennen.</p>
      <i>Textzeilen, die nicht den obigen Regeln entsprechen, werden ignoriert.</i>
  `,
      useRaptor: 'RAPTOR zur Verbesserung des Abrufs verwenden',
      useRaptorTip:
        'RAPTOR für Multi-Hop-Frage-Antwort-Aufgaben aktivieren. Details unter https://ragflow.io/docs/dev/enable_raptor.',
      prompt: 'Prompt',
      promptTip:
        'Verwenden Sie den Systemprompt, um die Aufgabe für das LLM zu beschreiben, festzulegen, wie es antworten soll, und andere verschiedene Anforderungen zu skizzieren. Der Systemprompt wird oft in Verbindung mit Schlüsseln (Variablen) verwendet, die als verschiedene Dateninputs für das LLM dienen. Verwenden Sie einen Schrägstrich `/` oder die (x)-Schaltfläche, um die zu verwendenden Schlüssel anzuzeigen.',
      promptMessage: 'Prompt ist erforderlich',
      promptText: `Bitte fassen Sie die folgenden Absätze zusammen. Seien Sie vorsichtig mit den Zahlen, erfinden Sie keine Dinge. Absätze wie folgt:
        {cluster_content}
  Das oben Genannte ist der Inhalt, den Sie zusammenfassen müssen.`,
      maxToken: 'Maximale Token',
      maxTokenTip:
        'Die maximale Anzahl an Token pro generiertem Zusammenfassungs-Chunk.',
      maxTokenMessage: 'Maximale Token sind erforderlich',
      threshold: 'Schwellenwert',
      thresholdTip:
        'In RAPTOR werden Chunks anhand ihrer semantischen Ähnlichkeit gruppiert. Der Schwellenwert-Parameter legt die minimale Ähnlichkeit fest, die erforderlich ist, damit Chunks zusammengefasst werden. Ein höherer Schwellenwert bedeutet weniger Chunks pro Cluster, während ein niedrigerer Wert mehr Chunks pro Cluster zulässt.',
      thresholdMessage: 'Schwellenwert ist erforderlich',
      maxCluster: 'Maximale Cluster',
      maxClusterTip: 'Die maximale Anzahl der zu erstellenden Cluster.',
      maxClusterMessage: 'Maximale Cluster sind erforderlich',
      randomSeed: 'Zufallszahl',
      randomSeedMessage: 'Zufallszahl ist erforderlich',
      entityTypes: 'Entitätstypen',
      vietnamese: 'Vietnamesisch',
      pageRank: 'PageRank',
      pageRankTip:
        'Sie können während des Abrufs bestimmten Wissensdatenbanken eine höhere PageRank-Bewertung zuweisen. Die entsprechende Bewertung wird zu den hybriden Ähnlichkeitswerten der abgerufenen Chunks aus diesen Wissensdatenbanken addiert, wodurch deren Ranking erhöht wird. Weitere Informationen finden Sie unter https://ragflow.io/docs/dev/set_page_rank.',
      tagName: 'Tag',
      frequency: 'Häufigkeit',
      searchTags: 'Tags durchsuchen',
      tagCloud: 'Wolke',
      tagTable: 'Tabelle',
      tagSet: 'Tag-Sets',
      tagSetTip: `
       <p> Wählen Sie eine oder mehrere Tag-Wissensdatenbanken aus, um Chunks in Ihrer Wissensdatenbank automatisch zu taggen. </p>
  <p>Die Benutzeranfrage wird ebenfalls automatisch getaggt.</p>
  Diese Auto-Tag-Funktion verbessert den Abruf, indem sie eine weitere Schicht domänenspezifischen Wissens zum vorhandenen Datensatz hinzufügt.
  <p>Unterschied zwischen Auto-Tag und Auto-Schlüsselwort:</p>
  <ul>
    <li>Eine Tag-Wissensdatenbank ist ein benutzerdefiniertes geschlossenes Set, während vom LLM extrahierte Schlüsselwörter als offenes Set betrachtet werden können.</li>
    <li>Sie müssen Tag-Sets in bestimmten Formaten hochladen, bevor Sie die Auto-Tag-Funktion ausführen.</li>
    <li>Die Auto-Schlüsselwort-Funktion ist vom LLM abhängig und verbraucht eine erhebliche Anzahl an Tokens.</li>
  </ul>
  <p>Siehe https://ragflow.io/docs/dev/use_tag_sets für Details.</p>
        `,
      topnTags: 'Top-N Tags',
      tags: 'Tags',
      addTag: 'Tag hinzufügen',
      useGraphRag: 'Wissensgraph extrahieren',
      useGraphRagTip:
        'Erstellen Sie einen Wissensgraph über Dateiabschnitte der aktuellen Wissensbasis, um die Beantwortung von Fragen mit mehreren Schritten und verschachtelter Logik zu verbessern. Weitere Informationen finden Sie unter https://ragflow.io/docs/dev/construct_knowledge_graph.',
      graphRagMethod: 'Methode',
      graphRagMethodTip: `Light: (Standard) Verwendet von github.com/HKUDS/LightRAG bereitgestellte Prompts, um Entitäten und Beziehungen zu extrahieren. Diese Option verbraucht weniger Tokens, weniger Speicher und weniger Rechenressourcen.</br>
          General: Verwendet von github.com/microsoft/graphrag bereitgestellte Prompts, um Entitäten und Beziehungen zu extrahieren`,
      resolution: 'Entitätsauflösung',
      resolutionTip: `Ein Entitäts-Deduplizierungsschalter. Wenn aktiviert, wird das LLM ähnliche Entitäten kombinieren - z.B. '2025' und 'das Jahr 2025' oder 'IT' und 'Informationstechnologie' - um einen genaueren Graphen zu konstruieren`,
      community: 'Generierung von Gemeinschaftsberichten',
      communityTip:
        'In einem Wissensgraphen ist eine Gemeinschaft ein Cluster von Entitäten, die durch Beziehungen verbunden sind. Sie können das LLM eine Zusammenfassung für jede Gemeinschaft erstellen lassen, bekannt als Gemeinschaftsbericht. Weitere Informationen finden Sie hier: https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/',
    },
    chunk: {
      chunk: 'Chunk',
      bulk: 'Masse',
      selectAll: 'Alle auswählen',
      enabledSelected: 'Ausgewählte aktivieren',
      disabledSelected: 'Ausgewählte deaktivieren',
      deleteSelected: 'Ausgewählte löschen',
      search: 'Suchen',
      all: 'Alle',
      enabled: 'Aktiviert',
      disabled: 'Deaktiviert',
      keyword: 'Schlüsselwort',
      function: 'Funktion',
      chunkMessage: 'Bitte Wert eingeben!',
      full: 'Volltext',
      ellipse: 'Ellipse',
      graph: 'Wissensgraph',
      mind: 'Mind Map',
      question: 'Frage',
      questionTip:
        'Wenn vorgegebene Fragen vorhanden sind, basiert das Embedding des Chunks auf diesen.',
    },
    chat: {
      newConversation: 'Neue Unterhaltung',
      createAssistant: 'Assistenten erstellen',
      assistantSetting: 'Assistenteneinstellung',
      promptEngine: 'Prompt-Engine',
      modelSetting: 'Modelleinstellung',
      chat: 'Chat',
      newChat: 'Neuer Chat',
      send: 'Senden',
      sendPlaceholder: 'Nachricht an den Assistenten...',
      chatConfiguration: 'Chat-Konfiguration',
      chatConfigurationDescription:
        'Richten Sie einen Chat-Assistenten für die ausgewählten Datensätze (Wissensbasen) hier ein! 💕',
      assistantName: 'Assistentenname',
      assistantNameMessage: 'Assistentenname ist erforderlich',
      namePlaceholder: 'z.B. Lebenslauf-Jarvis',
      assistantAvatar: 'Assistentenbild',
      language: 'Sprache',
      emptyResponse: 'Leere Antwort',
      emptyResponseTip:
        'Legen Sie dies als Antwort fest, wenn keine Ergebnisse aus den Wissensdatenbanken für Ihre Anfrage abgerufen werden, oder lassen Sie dieses Feld leer, damit das LLM improvisieren kann, wenn nichts gefunden wird.',
      emptyResponseMessage:
        'Eine leere Antwort wird ausgelöst, wenn nichts Relevantes aus den Wissensdatenbanken abgerufen wird. Sie müssen das Feld "Leere Antwort" löschen, wenn keine Wissensdatenbank ausgewählt ist.',
      setAnOpener: 'Begrüßungstext',
      setAnOpenerInitial:
        'Hallo! Ich bin Ihr Assistent, was kann ich für Sie tun?',
      setAnOpenerTip: 'Legen Sie einen Begrüßungstext für Benutzer fest.',
      knowledgeBases: 'Wissensdatenbanken',
      knowledgeBasesMessage: 'Bitte auswählen',
      knowledgeBasesTip:
        'Wählen Sie die Wissensdatenbanken aus, die mit diesem Chat-Assistenten verknüpft werden sollen. Eine leere Wissensdatenbank wird nicht in der Dropdown-Liste angezeigt.',
      system: 'System',
      systemInitialValue:
        'Sie sind ein intelligenter Assistent. Bitte fassen Sie den Inhalt der Wissensdatenbank zusammen, um die Frage zu beantworten. Bitte listen Sie die Daten in der Wissensdatenbank auf und antworten Sie detailliert. Wenn alle Inhalte der Wissensdatenbank für die Frage irrelevant sind, muss Ihre Antwort den Satz "Die gesuchte Antwort wurde in der Wissensdatenbank nicht gefunden!" enthalten. Antworten müssen den Chat-Verlauf berücksichtigen.\nHier ist die Wissensdatenbank:\n{knowledge}\nDas oben Genannte ist die Wissensdatenbank.',
      systemMessage: 'Bitte eingeben!',
      systemTip:
        'Ihre Prompts oder Anweisungen für das LLM, einschließlich, aber nicht beschränkt auf seine Rolle, die gewünschte Länge, den Ton und die Sprache seiner Antworten. Wenn Ihr Modell native Unterstützung für das Schlussfolgern hat, können Sie //no_thinking zum Prompt hinzufügen, um das Schlussfolgern zu stoppen.',
      topN: 'Top N',
      topNTip:
        'Nicht alle Chunks mit einem Ähnlichkeitswert über dem "Ähnlichkeitsschwellenwert" werden an das LLM gesendet. Dies wählt die "Top N" Chunks aus den abgerufenen aus.',
      variable: 'Variable',
      variableTip:
        'In Kombination mit den APIs zur Verwaltung von Chat-Assistenten von RAGFlow können Variablen dazu beitragen, flexiblere System-Prompt-Strategien zu entwickeln. Die definierten Variablen werden von „System-Prompt“ als Teil der Prompts für das LLM verwendet. {knowledge} ist eine spezielle reservierte Variable, die Teile darstellt, die aus den angegebenen Wissensbasen abgerufen werden, und alle Variablen sollten in geschweiften Klammern {} im „System-Prompt“ eingeschlossen werden. Weitere Informationen finden Sie unter https://ragflow.io/docs/dev/set_chat_variables.',
      add: 'Hinzufügen',
      key: 'Schlüssel',
      optional: 'Optional',
      operation: 'Operation',
      model: 'Modell',
      modelTip: 'Großes Sprachmodell für Chat',
      modelMessage: 'Bitte auswählen!',
      freedom: 'Freiheit',
      improvise: 'Improvisieren',
      precise: 'Präzise',
      balance: 'Ausgewogen',
      freedomTip:
        'Eine Abkürzung für die Einstellungen "Temperatur", "Top P", "Präsenzstrafe" und "Häufigkeitsstrafe", die den Freiheitsgrad des Modells angibt. Dieser Parameter hat drei Optionen: Wählen Sie "Improvisieren", um kreativere Antworten zu erzeugen; wählen Sie "Präzise" (Standard), um konservativere Antworten zu erzeugen; "Ausgewogen" ist ein Mittelweg zwischen "Improvisieren" und "Präzise".',
      temperature: 'Temperatur',
      temperatureMessage: 'Temperatur ist erforderlich',
      temperatureTip:
        'Dieser Parameter steuert die Zufälligkeit der Vorhersagen des Modells. Eine niedrigere Temperatur führt zu konservativeren Antworten, während eine höhere Temperatur kreativere und vielfältigere Antworten liefert.',
      topP: 'Top P',
      topPMessage: 'Top P ist erforderlich',
      topPTip:
        'Auch bekannt als "Nucleus-Sampling", setzt dieser Parameter einen Schwellenwert für die Auswahl einer kleineren Menge der wahrscheinlichsten Wörter, aus denen Stichproben genommen werden sollen, und schneidet die weniger wahrscheinlichen ab.',
      presencePenalty: 'Präsenzstrafe',
      presencePenaltyMessage: 'Präsenzstrafe ist erforderlich',
      presencePenaltyTip:
        'Dies entmutigt das Modell, dieselben Informationen zu wiederholen, indem es Wörter bestraft, die bereits im Gespräch vorgekommen sind.',
      frequencyPenalty: 'Häufigkeitsstrafe',
      frequencyPenaltyMessage: 'Häufigkeitsstrafe ist erforderlich',
      frequencyPenaltyTip:
        'Ähnlich wie die Präsenzstrafe reduziert dies die Tendenz des Modells, dieselben Wörter häufig zu wiederholen.',
      maxTokens: 'Maximale Tokens',
      maxTokensMessage: 'Maximale Tokens sind erforderlich',
      maxTokensTip:
        'Dies legt die maximale Länge der Ausgabe des Modells fest, gemessen an der Anzahl der Tokens (Wörter oder Wortteile). Standardmäßig 512. Wenn deaktiviert, heben Sie die maximale Token-Begrenzung auf und erlauben dem Modell, die Anzahl der Tokens in seinen Antworten selbst zu bestimmen.',
      maxTokensInvalidMessage:
        'Bitte geben Sie eine gültige Zahl für Maximale Tokens ein.',
      maxTokensMinMessage: 'Maximale Tokens können nicht weniger als 0 sein.',
      quote: 'Zitat anzeigen',
      quoteTip: 'Ob der Originaltext als Referenz angezeigt werden soll.',
      selfRag: 'Self-RAG',
      selfRagTip:
        'Bitte beziehen Sie sich auf: https://huggingface.co/papers/2310.11511',
      overview: 'Chat-ID',
      pv: 'Anzahl der Nachrichten',
      uv: 'Anzahl aktiver Benutzer',
      speed: 'Token-Ausgabegeschwindigkeit',
      tokens: 'Verbrauchte Token-Anzahl',
      round: 'Anzahl der Sitzungsinteraktionen',
      thumbUp: 'Kundenzufriedenheit',
      preview: 'Vorschau',
      embedded: 'Eingebettet',
      serviceApiEndpoint: 'Service-API-Endpunkt',
      apiKey: 'API-SCHLÜSSEL',
      apiReference: 'API-Dokumente',
      dateRange: 'Datumsbereich:',
      backendServiceApi: 'API-Server',
      createNewKey: 'Neuen Schlüssel erstellen',
      created: 'Erstellt',
      action: 'Aktion',
      embedModalTitle: 'In Webseite einbetten',
      comingSoon: 'Demnächst verfügbar',
      fullScreenTitle: 'Vollständige Einbettung',
      fullScreenDescription:
        'Betten Sie den folgenden iframe an der gewünschten Stelle in Ihre Website ein',
      partialTitle: 'Teilweise Einbettung',
      extensionTitle: 'Chrome-Erweiterung',
      tokenError: 'Bitte erstellen Sie zuerst einen API-Schlüssel.',
      betaError:
        'Bitte erwerben Sie zuerst einen RAGFlow-API-Schlüssel auf der Systemeinstellungsseite.',
      searching: 'Suche...',
      parsing: 'Analysiere',
      uploading: 'Hochladen',
      uploadFailed: 'Hochladen fehlgeschlagen',
      regenerate: 'Neu generieren',
      read: 'Inhalt lesen',
      tts: 'Text zu Sprache',
      ttsTip:
        'Stellen Sie sicher, dass Sie ein TTS-Modell auf der Einstellungsseite auswählen, bevor Sie diesen Schalter aktivieren, um Text als Audio abzuspielen.',
      relatedQuestion: 'Verwandte Frage',
      answerTitle: 'A',
      multiTurn: 'Mehrfach-Runden-Optimierung',
      multiTurnTip:
        'Dies optimiert Benutzeranfragen unter Verwendung des Kontexts in einer mehrrundigen Unterhaltung. Wenn aktiviert, werden zusätzliche LLM-Tokens verbraucht.',
      howUseId: 'Wie verwendet man die Chat-ID?',
      description: 'Beschreibung des Assistenten',
      descriptionPlaceholder: 'z.B. Ein Chat-Assistent für Lebensläufe.',
      useKnowledgeGraph: 'Wissensgraph verwenden',
      useKnowledgeGraphTip:
        'Ob ein Wissensgraph im angegebenen Wissensspeicher während der Wiederherstellung für die Beantwortung von Fragen mit mehreren Schritten verwendet werden soll. Wenn aktiviert, beinhaltet dies iterative Suchen über Entitäten-, Beziehungs- und Gemeinschaftsberichtssegmente, was die Wiederherstellungszeit erheblich verlängert.',
      keyword: 'Schlüsselwortanalyse',
      keywordTip:
        'LLM anwenden, um die Fragen des Benutzers zu analysieren und Schlüsselwörter zu extrahieren, die während der Relevanzberechnung hervorgehoben werden.',
      languageTip:
        'Ermöglicht die Umformulierung von Sätzen in der angegebenen Sprache oder verwendet standardmäßig die letzte Frage, wenn keine ausgewählt ist.',
      avatarHidden: 'Avatar ausblenden',
      locale: 'Gebietsschema',
      selectLanguage: 'Sprache auswählen',
      reasoning: 'Schlussfolgerung',
      reasoningTip:
        'Ob beim Frage-Antwort-Prozess ein logisches Arbeitsverfahren aktiviert werden soll, wie es bei Modellen wie Deepseek-R1 oder OpenAI o1 der Fall ist. Wenn aktiviert, ermöglicht diese Funktion dem Modell, auf externes Wissen zuzugreifen und komplexe Fragen schrittweise mithilfe von Techniken wie der „Chain-of-Thought“-Argumentation zu lösen. Durch die Zerlegung von Problemen in überschaubare Schritte verbessert dieser Ansatz die Fähigkeit des Modells, präzise Antworten zu liefern, was die Leistung bei Aufgaben, die logisches Denken und mehrschrittige Überlegungen erfordern, steigert.',
      tavilyApiKeyTip:
        'Wenn hier ein API-Schlüssel korrekt eingestellt ist, werden Tavily-basierte Websuchen verwendet, um den Abruf aus der Wissensdatenbank zu ergänzen.',
      tavilyApiKeyMessage: 'Bitte geben Sie Ihren Tavily-API-Schlüssel ein',
      tavilyApiKeyHelp: 'Wie bekomme ich ihn?',
    },
    setting: {
      profile: 'Profil',
      profileDescription:
        'Aktualisieren Sie hier Ihr Foto und Ihre persönlichen Daten.',
      maxTokens: 'Maximale Tokens',
      maxTokensMessage: 'Maximale Tokens sind erforderlich',
      maxTokensTip:
        'Dies legt die maximale Länge der Ausgabe des Modells fest, gemessen an der Anzahl der Tokens (Wörter oder Wortteile). Standardmäßig 512. Wenn deaktiviert, heben Sie die maximale Token-Begrenzung auf und erlauben dem Modell, die Anzahl der Tokens in seinen Antworten selbst zu bestimmen.',
      maxTokensInvalidMessage:
        'Bitte geben Sie eine gültige Zahl für Maximale Tokens ein.',
      maxTokensMinMessage: 'Maximale Tokens können nicht weniger als 0 sein.',
      password: 'Passwort',
      passwordDescription:
        'Bitte geben Sie Ihr aktuelles Passwort ein, um Ihr Passwort zu ändern.',
      model: 'Modellanbieter',
      modelDescription:
        'Legen Sie hier die Modellparameter und den API-SCHLÜSSEL fest.',
      team: 'Team',
      system: 'System',
      logout: 'Abmelden',
      api: 'API',
      username: 'Benutzername',
      usernameMessage: 'Bitte geben Sie Ihren Benutzernamen ein!',
      photo: 'Ihr Foto',
      photoDescription: 'Dies wird in Ihrem Profil angezeigt.',
      colorSchema: 'Farbschema',
      colorSchemaMessage: 'Bitte wählen Sie Ihr Farbschema!',
      colorSchemaPlaceholder: 'Wählen Sie Ihr Farbschema',
      bright: 'Hell',
      dark: 'Dunkel',
      timezone: 'Zeitzone',
      timezoneMessage: 'Bitte geben Sie Ihre Zeitzone ein!',
      timezonePlaceholder: 'Wählen Sie Ihre Zeitzone',
      email: 'E-Mail-Adresse',
      emailDescription:
        'Nach der Registrierung kann die E-Mail nicht mehr geändert werden.',
      currentPassword: 'Aktuelles Passwort',
      currentPasswordMessage: 'Bitte geben Sie Ihr Passwort ein!',
      newPassword: 'Neues Passwort',
      newPasswordMessage: 'Bitte geben Sie Ihr Passwort ein!',
      newPasswordDescription:
        'Ihr neues Passwort muss mehr als 8 Zeichen haben.',
      confirmPassword: 'Neues Passwort bestätigen',
      confirmPasswordMessage: 'Bitte bestätigen Sie Ihr Passwort!',
      confirmPasswordNonMatchMessage:
        'Die eingegebenen neuen Passwörter stimmen nicht überein!',
      cancel: 'Abbrechen',
      addedModels: 'Hinzugefügte Modelle',
      modelsToBeAdded: 'Hinzuzufügende Modelle',
      addTheModel: 'Modell hinzufügen',
      apiKey: 'API-Schlüssel',
      apiKeyMessage:
        'Bitte geben Sie den API-Schlüssel ein (für lokal bereitgestellte Modelle ignorieren Sie dies).',
      apiKeyTip:
        'Der API-Schlüssel kann durch Registrierung beim entsprechenden LLM-Anbieter erhalten werden.',
      showMoreModels: 'Mehr Modelle anzeigen',
      baseUrl: 'Basis-URL',
      baseUrlTip:
        'Wenn Ihr API-Schlüssel von OpenAI stammt, ignorieren Sie dies. Andere Zwischenanbieter geben diese Basis-URL mit dem API-Schlüssel an.',
      modify: 'Ändern',
      systemModelSettings: 'Standardmodelle festlegen',
      chatModel: 'Chat-Modell',
      chatModelTip:
        'Das Standard-Chat-LLM, das alle neu erstellten Wissensdatenbanken verwenden werden.',
      embeddingModel: 'Embedding-Modell',
      embeddingModelTip:
        'Das Standard-Einbettungsmodell für jede neu erstellte Wissensdatenbank. Wenn Sie kein Einbettungsmodell in der Dropdown-Liste finden, prüfen Sie, ob Sie die RAGFlow Slim Edition verwenden (die keine Einbettungsmodelle enthält), oder überprüfen Sie https://ragflow.io/docs/dev/supported_models, um zu sehen, ob Ihr Modellanbieter dieses Modell unterstützt.',
      img2txtModel: 'Img2txt-Modell',
      img2txtModelTip:
        'Das Standardmodell img2txt für jede neu erstellte Wissensdatenbank. Es beschreibt ein Bild oder Video. Wenn Sie kein Modell im Dropdown-Menü finden können, überprüfen Sie https://ragflow.io/docs/dev/supported_models, um zu sehen, ob Ihr Modellanbieter dieses Modell unterstützt.',
      sequence2txtModel: 'Sequence2txt-Modell',
      sequence2txtModelTip:
        'Das Standard-ASR-Modell, das alle neu erstellten Wissensdatenbanken verwenden werden. Verwenden Sie dieses Modell, um Stimmen in entsprechenden Text zu übersetzen. Wenn Sie kein Modell im Dropdown-Menü finden können, überprüfen Sie https://ragflow.io/docs/dev/supported_models, um zu sehen, ob Ihr Modellanbieter dieses Modell unterstützt.',
      rerankModel: 'Rerank-Modell',
      rerankModelTip:
        'Das Standard-Rerank-Modell zum Reranking von Textabschnitten. Wenn Sie kein Modell im Dropdown-Menü finden, überprüfen Sie https://ragflow.io/docs/dev/supported_models, um zu sehen, ob Ihr Modellanbieter dieses Modell unterstützt.',
      ttsModel: 'TTS-Modell',
      ttsModelTip:
        'Das Standard-Text-to-Speech-Modell. Wenn Sie kein Modell im Dropdown-Menü finden, überprüfen Sie https://ragflow.io/docs/dev/supported_models, um zu sehen, ob Ihr Modellanbieter dieses Modell unterstützt.',
      workspace: 'Arbeitsbereich',
      upgrade: 'Upgrade',
      addLlmTitle: 'LLM hinzufügen',
      modelName: 'Modellname',
      modelID: 'Modell-ID',
      modelUid: 'Modell-UID',
      modelNameMessage: 'Bitte geben Sie Ihren Modellnamen ein!',
      modelType: 'Modelltyp',
      modelTypeMessage: 'Bitte geben Sie Ihren Modelltyp ein!',
      addLlmBaseUrl: 'Basis-URL',
      baseUrlNameMessage: 'Bitte geben Sie Ihre Basis-URL ein!',
      vision: 'Unterstützt es Vision?',
      ollamaLink: 'Wie integriere ich {{name}}',
      FishAudioLink: 'Wie verwende ich FishAudio',
      TencentCloudLink: 'Wie verwende ich TencentCloud ASR',
      volcModelNameMessage: 'Bitte geben Sie Ihren Modellnamen ein!',
      addEndpointID: 'EndpointID des Modells',
      endpointIDMessage: 'Bitte geben Sie Ihre EndpointID des Modells ein',
      addArkApiKey: 'VOLC ARK_API_KEY',
      ArkApiKeyMessage: 'Bitte geben Sie Ihren ARK_API_KEY ein',
      bedrockModelNameMessage: 'Bitte geben Sie Ihren Modellnamen ein!',
      addBedrockEngineAK: 'ZUGRIFFSSCHLÜSSEL',
      bedrockAKMessage: 'Bitte geben Sie Ihren ZUGRIFFSSCHLÜSSEL ein',
      addBedrockSK: 'GEHEIMER SCHLÜSSEL',
      bedrockSKMessage: 'Bitte geben Sie Ihren GEHEIMEN SCHLÜSSEL ein',
      bedrockRegion: 'AWS-Region',
      bedrockRegionMessage: 'Bitte auswählen!',
      'us-east-1': 'US-Ost (N. Virginia)',
      'us-west-2': 'US-West (Oregon)',
      'ap-southeast-1': 'Asien-Pazifik (Singapur)',
      'ap-northeast-1': 'Asien-Pazifik (Tokio)',
      'eu-central-1': 'Europa (Frankfurt)',
      'us-gov-west-1': 'AWS GovCloud (US-West)',
      'ap-southeast-2': 'Asien-Pazifik (Sydney)',
      addHunyuanSID: 'Hunyuan Secret ID',
      HunyuanSIDMessage: 'Bitte geben Sie Ihre Secret ID ein',
      addHunyuanSK: 'Hunyuan Secret Key',
      HunyuanSKMessage: 'Bitte geben Sie Ihren Secret Key ein',
      addTencentCloudSID: 'TencentCloud Secret ID',
      TencentCloudSIDMessage: 'Bitte geben Sie Ihre Secret ID ein',
      addTencentCloudSK: 'TencentCloud Secret Key',
      TencentCloudSKMessage: 'Bitte geben Sie Ihren Secret Key ein',
      SparkModelNameMessage: 'Bitte wählen Sie das Spark-Modell',
      addSparkAPIPassword: 'Spark APIPassword',
      SparkAPIPasswordMessage: 'Bitte geben Sie Ihr APIPassword ein',
      addSparkAPPID: 'Spark APP ID',
      SparkAPPIDMessage: 'Bitte geben Sie Ihre APP ID ein',
      addSparkAPISecret: 'Spark APISecret',
      SparkAPISecretMessage: 'Bitte geben Sie Ihr APISecret ein',
      addSparkAPIKey: 'Spark APIKey',
      SparkAPIKeyMessage: 'Bitte geben Sie Ihren APIKey ein',
      yiyanModelNameMessage: 'Bitte geben Sie den Modellnamen ein',
      addyiyanAK: 'yiyan API KEY',
      yiyanAKMessage: 'Bitte geben Sie Ihren API KEY ein',
      addyiyanSK: 'yiyan Secret KEY',
      yiyanSKMessage: 'Bitte geben Sie Ihren Secret KEY ein',
      FishAudioModelNameMessage:
        'Bitte geben Sie Ihrem Sprachsynthesemodell einen Namen',
      addFishAudioAK: 'Fish Audio API KEY',
      addFishAudioAKMessage: 'Bitte geben Sie Ihren API KEY ein',
      addFishAudioRefID: 'FishAudio Referenz-ID',
      addFishAudioRefIDMessage:
        'Bitte geben Sie die Referenz-ID ein (lassen Sie das Feld leer, um das Standardmodell zu verwenden).',
      GoogleModelIDMessage: 'Bitte geben Sie Ihre Modell-ID ein!',
      addGoogleProjectID: 'Projekt-ID',
      GoogleProjectIDMessage: 'Bitte geben Sie Ihre Projekt-ID ein',
      addGoogleServiceAccountKey:
        'Dienstkontoschlüssel (Lassen Sie das Feld leer, wenn Sie Anwendungsstandardanmeldedaten verwenden)',
      GoogleServiceAccountKeyMessage:
        'Bitte geben Sie den Google Cloud Dienstkontoschlüssel im base64-Format ein',
      addGoogleRegion: 'Google Cloud Region',
      GoogleRegionMessage: 'Bitte geben Sie die Google Cloud Region ein',
      modelProvidersWarn:
        'Bitte fügen Sie zuerst sowohl das Embedding-Modell als auch das LLM in <b>Einstellungen > Modellanbieter</b> hinzu. Legen Sie sie dann in "Systemmodelleinstellungen" fest.',
      apiVersion: 'API-Version',
      apiVersionMessage: 'Bitte geben Sie die API-Version ein',
      add: 'Hinzufügen',
      updateDate: 'Aktualisierungsdatum',
      role: 'Rolle',
      invite: 'Einladen',
      agree: 'Akzeptieren',
      refuse: 'Ablehnen',
      teamMembers: 'Teammitglieder',
      joinedTeams: 'Beigetretene Teams',
      sureDelete:
        'Sind Sie sicher, dass Sie dieses Mitglied entfernen möchten?',
      quit: 'Verlassen',
      sureQuit:
        'Sind Sie sicher, dass Sie das Team, dem Sie beigetreten sind, verlassen möchten?',
      modelsToBeAddedTooltip:
        'Wenn Ihr Modellanbieter nicht aufgeführt ist, aber behauptet, „OpenAI-kompatibel“ zu sein, wählen Sie die Karte OpenAI-API-compatible, um das/die entsprechende(n) Modell(e) hinzuzufügen.',
    },
    message: {
      registered: 'Registriert!',
      logout: 'Abgemeldet',
      logged: 'Angemeldet!',
      pleaseSelectChunk: 'Bitte wählen Sie einen Chunk aus!',
      modified: 'Geändert',
      created: 'Erstellt',
      deleted: 'Gelöscht',
      renamed: 'Umbenannt',
      operated: 'Ausgeführt',
      updated: 'Aktualisiert',
      uploaded: 'Hochgeladen',
      200: 'Der Server gibt die angeforderten Daten erfolgreich zurück.',
      201: 'Daten erfolgreich erstellt oder geändert.',
      202: 'Eine Anfrage wurde im Hintergrund in die Warteschlange gestellt (asynchrone Aufgabe).',
      204: 'Daten erfolgreich gelöscht.',
      400: 'Bei der gestellten Anfrage ist ein Fehler aufgetreten, und der Server hat keine Daten erstellt oder geändert.',
      401: 'Bitte melden Sie sich erneut an.',
      403: 'Der Benutzer ist autorisiert, aber der Zugriff ist verboten.',
      404: 'Die Anfrage wurde für einen nicht existierenden Datensatz gestellt, und der Server hat den Vorgang nicht ausgeführt.',
      406: 'Das angeforderte Format ist nicht verfügbar.',
      410: 'Die angeforderte Ressource wurde dauerhaft gelöscht und wird nicht mehr verfügbar sein.',
      413: 'Die Gesamtgröße der auf einmal hochgeladenen Dateien ist zu groß.',
      422: 'Beim Erstellen eines Objekts ist ein Validierungsfehler aufgetreten.',
      500: 'Ein Serverfehler ist aufgetreten, bitte überprüfen Sie den Server.',
      502: 'Gateway-Fehler.',
      503: 'Der Dienst ist nicht verfügbar und der Server ist vorübergehend überlastet oder wird gewartet.',
      504: 'Gateway-Timeout.',
      requestError: 'Anfragefehler',
      networkAnomalyDescription:
        'Es liegt eine Anomalie in Ihrem Netzwerk vor und Sie können keine Verbindung zum Server herstellen.',
      networkAnomaly: 'Netzwerkanomalie',
      hint: 'Hinweis',
    },
    fileManager: {
      name: 'Name',
      uploadDate: 'Hochladedatum',
      knowledgeBase: 'Wissensdatenbank',
      size: 'Größe',
      action: 'Aktion',
      addToKnowledge: 'Mit Wissensdatenbank verknüpfen',
      pleaseSelect: 'Bitte auswählen',
      newFolder: 'Neuer Ordner',
      file: 'Datei',
      uploadFile: 'Datei hochladen',
      parseOnCreation: 'Bei Erstellung analysieren',
      directory: 'Verzeichnis',
      uploadTitle: 'Ziehen Sie Ihre Datei hierher, um sie hochzuladen',
      uploadDescription:
        'RAGFlow unterstützt das Hochladen von Dateien einzeln oder in Batches. Für lokal bereitgestelltes RAGFlow: Die maximale Dateigröße pro Upload beträgt 1 GB, mit einem Batch-Upload-Limit von 32 Dateien. Es gibt keine Begrenzung der Gesamtanzahl an Dateien pro Konto. Für demo.ragflow.io: Die maximale Dateigröße pro Upload beträgt 10 MB, wobei jede Datei nicht größer als 10 MB sein darf und maximal 128 Dateien pro Konto erlaubt sind.',
      local: 'Lokale Uploads',
      s3: 'S3-Uploads',
      preview: 'Vorschau',
      fileError: 'Dateifehler',
      uploadLimit:
        'Jede Datei darf 10MB nicht überschreiten, und die Gesamtzahl der Dateien darf 128 nicht überschreiten.',
      destinationFolder: 'Zielordner',
    },
    flow: {
      cite: 'Zitieren',
      citeTip: 'Zitiertipp',
      name: 'Name',
      nameMessage: 'Bitte Namen eingeben',
      description: 'Beschreibung',
      examples: 'Beispiele',
      to: 'Zu',
      msg: 'Nachrichten',
      messagePlaceholder: 'Nachricht',
      messageMsg: 'Bitte Nachricht eingeben oder dieses Feld löschen.',
      addField: 'Option hinzufügen',
      addMessage: 'Nachricht hinzufügen',
      loop: 'Schleife',
      loopTip:
        'Schleife ist die Obergrenze der Anzahl der Durchläufe der aktuellen Komponente. Wenn die Anzahl der Durchläufe den Wert der Schleife überschreitet, bedeutet dies, dass die Komponente die aktuelle Aufgabe nicht abschließen kann. Bitte optimieren Sie den Agenten neu',
      yes: 'Ja',
      no: 'Nein',
      key: 'Schlüssel',
      componentId: 'Komponenten-ID',
      add: 'Hinzufügen',
      operation: 'Operation',
      run: 'Ausführen',
      save: 'Speichern',
      title: 'ID:',
      beginDescription: 'Hier beginnt der Ablauf.',
      answerDescription:
        'Eine Komponente, die als Schnittstelle zwischen Mensch und Bot dient, Benutzereingaben empfängt und die Antworten des Agenten anzeigt.',
      retrievalDescription:
        'Eine Komponente, die Informationen aus bestimmten Wissensdatenbanken (Datensätzen) abruft. Stellen Sie sicher, dass die von Ihnen ausgewählten Wissensdatenbanken dasselbe Embedding-Modell verwenden.',
      generateDescription:
        'Eine Komponente, die das LLM auffordert, Antworten zu generieren. Stellen Sie sicher, dass der Prompt korrekt eingestellt ist.',
      categorizeDescription:
        'Eine Komponente, die das LLM verwendet, um Benutzereingaben in vordefinierte Kategorien zu klassifizieren. Stellen Sie sicher, dass Sie für jede Kategorie den Namen, die Beschreibung und Beispiele sowie die entsprechende nächste Komponente angeben.',
      relevantDescription:
        'Eine Komponente, die das LLM verwendet, um zu beurteilen, ob die vorgelagerte Ausgabe für die neueste Anfrage des Benutzers relevant ist. Stellen Sie sicher, dass Sie die nächste Komponente für jedes Beurteilungsergebnis angeben.',
      rewriteQuestionDescription:
        'Eine Komponente, die eine Benutzeranfrage aus der Interaktionskomponente basierend auf dem Kontext vorheriger Dialoge umformuliert.',
      messageDescription:
        'Eine Komponente, die eine statische Nachricht sendet. Wenn mehrere Nachrichten bereitgestellt werden, wählt sie zufällig eine zum Senden aus. Stellen Sie sicher, dass ihr nachgelagerter Bereich "Interact" ist, die Schnittstellenkomponente.',
      keywordDescription:
        'Eine Komponente, die die Top-N-Suchergebnisse aus der Benutzereingabe abruft. Stellen Sie sicher, dass der TopN-Wert vor der Verwendung richtig eingestellt ist.',
      switchDescription:
        'Eine Komponente, die Bedingungen basierend auf der Ausgabe vorheriger Komponenten auswertet und den Ausführungsfluss entsprechend lenkt. Sie ermöglicht komplexe Verzweigungslogik, indem Fälle definiert und Aktionen für jeden Fall oder Standardaktionen festgelegt werden, wenn keine Bedingungen erfüllt sind.',
      wikipediaDescription:
        'Eine Komponente, die auf wikipedia.org sucht und mit TopN die Anzahl der Suchergebnisse angibt. Sie ergänzt die vorhandenen Wissensdatenbanken.',
      promptText:
        'Bitte fassen Sie die folgenden Absätze zusammen. Seien Sie vorsichtig mit den Zahlen, erfinden Sie nichts. Absätze wie folgt:\n{input}\nDas oben ist der Inhalt, den Sie zusammenfassen müssen.',
      createGraph: 'Agenten erstellen',
      createFromTemplates: 'Aus Vorlagen erstellen',
      retrieval: 'Abruf',
      generate: 'Generieren',
      answer: 'Interagieren',
      categorize: 'Kategorisieren',
      relevant: 'Relevant',
      rewriteQuestion: 'Umschreiben',
      rewrite: 'Umschreiben',
      begin: 'Beginn',
      message: 'Nachricht',
      blank: 'Leer',
      createFromNothing: 'Erstellen Sie Ihren Agenten von Grund auf',
      addItem: 'Element hinzufügen',
      addSubItem: 'Unterelement hinzufügen',
      nameRequiredMsg: 'Name ist erforderlich',
      nameRepeatedMsg: 'Der Name darf nicht wiederholt werden',
      keywordExtract: 'Schlüsselwort',
      keywordExtractDescription:
        'Eine Komponente, die Schlüsselwörter aus einer Benutzeranfrage extrahiert, wobei Top N die Anzahl der zu extrahierenden Schlüsselwörter angibt.',
      baidu: 'Baidu',
      baiduDescription:
        'Eine Komponente, die auf baidu.com sucht und mit TopN die Anzahl der Suchergebnisse angibt. Sie ergänzt die vorhandenen Wissensdatenbanken.',
      duckDuckGo: 'DuckDuckGo',
      duckDuckGoDescription:
        'Eine Komponente, die auf duckduckgo.com sucht und Ihnen ermöglicht, die Anzahl der Suchergebnisse mit TopN anzugeben. Sie ergänzt die vorhandenen Wissensdatenbanken.',
      channel: 'Kanal',
      channelTip:
        'Führt eine Textsuche oder Nachrichtensuche für die Eingabe der Komponente durch',
      text: 'Text',
      news: 'Nachrichten',
      messageHistoryWindowSize: 'Nachrichtenfenstergröße',
      messageHistoryWindowSizeTip:
        'Die Fenstergröße des für das LLM sichtbaren Gesprächsverlaufs. Größer ist besser, aber achten Sie auf das maximale Token-Limit des LLM.',
      relevance: 'Relevanz',
      google: 'Google',
      googleDescription:
        'Eine Komponente, die auf https://www.google.com/ sucht und Ihnen ermöglicht, die Anzahl der Suchergebnisse mit TopN anzugeben. Sie ergänzt die vorhandenen Wissensdatenbanken. Bitte beachten Sie, dass hierfür ein API-Schlüssel von serpapi.com erforderlich ist.',
      bing: 'Bing',
      bingDescription:
        'Eine Komponente, die auf https://www.bing.com/ sucht und Ihnen ermöglicht, die Anzahl der Suchergebnisse mit TopN anzugeben. Sie ergänzt die vorhandenen Wissensdatenbanken. Bitte beachten Sie, dass hierfür ein API-Schlüssel von microsoft.com erforderlich ist.',
      apiKey: 'API-SCHLÜSSEL',
      country: 'Land & Region',
      language: 'Sprache',
      googleScholar: 'Google Scholar',
      googleScholarDescription:
        'Eine Komponente, die auf https://scholar.google.com/ sucht. Sie können Top N verwenden, um die Anzahl der Suchergebnisse anzugeben.',
      yearLow: 'Jahr Minimum',
      yearHigh: 'Jahr Maximum',
      patents: 'Patente',
      data: 'Daten',
      deepL: 'DeepL',
      deepLDescription:
        'Eine Komponente, die spezialisierte Übersetzungen von https://www.deepl.com/ abruft.',
      authKey: 'Authentifizierungsschlüssel',
      sourceLang: 'Quellsprache',
      targetLang: 'Zielsprache',
      gitHub: 'GitHub',
      gitHubDescription:
        'Eine Komponente, die nach Repositories auf https://github.com/ sucht. Sie können Top N verwenden, um die Anzahl der Suchergebnisse anzugeben.',
      baiduFanyi: 'BaiduFanyi',
      baiduFanyiDescription:
        'Eine Komponente, die spezialisierte Übersetzungen von https://fanyi.baidu.com/ abruft.',
      appid: 'App-ID',
      secretKey: 'Geheimer Schlüssel',
      domain: 'Domäne',
      transType: 'Übersetzungstyp',
      baiduSecretKeyOptions: {
        translate: 'Allgemeine Übersetzung',
        fieldtranslate: 'Fachübersetzung',
      },
      baiduDomainOptions: {
        it: 'Informationstechnologie',
        finance: 'Finanzen und Wirtschaft',
        machinery: 'Maschinenbau',
        senimed: 'Biomedizin',
        novel: 'Online-Literatur',
        academic: 'Wissenschaftliche Arbeit',
        aerospace: 'Luft- und Raumfahrt',
        wiki: 'Geistes- und Sozialwissenschaften',
        news: 'Nachrichten und Informationen',
        law: 'Gesetze und Vorschriften',
        contract: 'Vertrag',
      },
      baiduSourceLangOptions: {
        auto: 'Automatisch erkennen',
        zh: 'Chinesisch',
        en: 'Englisch',
        yue: 'Kantonesisch',
        wyw: 'Klassisches Chinesisch',
        jp: 'Japanisch',
        kor: 'Koreanisch',
        fra: 'Französisch',
        spa: 'Spanisch',
        th: 'Thailändisch',
        ara: 'Arabisch',
        ru: 'Russisch',
        pt: 'Portugiesisch',
        de: 'Deutsch',
        it: 'Italienisch',
        el: 'Griechisch',
        nl: 'Niederländisch',
        pl: 'Polnisch',
        bul: 'Bulgarisch',
        est: 'Estnisch',
        dan: 'Dänisch',
        fin: 'Finnisch',
        cs: 'Tschechisch',
        rom: 'Rumänisch',
        slo: 'Slowenisch',
        swe: 'Schwedisch',
        hu: 'Ungarisch',
        cht: 'Traditionelles Chinesisch',
        vie: 'Vietnamesisch',
      },
      qWeather: 'QWeather',
      qWeatherDescription:
        'Eine Komponente, die Wetterinformationen wie Temperatur und Luftqualität von https://www.qweather.com/ abruft.',
      lang: 'Sprache',
      type: 'Typ',
      webApiKey: 'Web-API-Schlüssel',
      userType: 'Benutzertyp',
      timePeriod: 'Zeitraum',
      qWeatherLangOptions: {
        zh: 'Vereinfachtes Chinesisch',
        'zh-hant': 'Traditionelles Chinesisch',
        en: 'Englisch',
        de: 'Deutsch',
        es: 'Spanisch',
        fr: 'Französisch',
        it: 'Italienisch',
        ja: 'Japanisch',
        ko: 'Koreanisch',
        ru: 'Russisch',
        hi: 'Hindi',
        th: 'Thailändisch',
        ar: 'Arabisch',
        pt: 'Portugiesisch',
        bn: 'Bengalisch',
        ms: 'Malaiisch',
        nl: 'Niederländisch',
        el: 'Griechisch',
        la: 'Lateinisch',
        sv: 'Schwedisch',
        id: 'Indonesisch',
        pl: 'Polnisch',
        tr: 'Türkisch',
        cs: 'Tschechisch',
        et: 'Estnisch',
        vi: 'Vietnamesisch',
        fil: 'Philippinisch',
        fi: 'Finnisch',
        he: 'Hebräisch',
        is: 'Isländisch',
        nb: 'Norwegisch',
      },
      qWeatherTypeOptions: {
        weather: 'Wettervorhersage',
        indices: 'Wetter-Lebensindex',
        airquality: 'Luftqualität',
      },
      qWeatherUserTypeOptions: {
        free: 'Kostenloser Abonnent',
        paid: 'Zahlender Abonnent',
      },
      qWeatherTimePeriodOptions: {
        now: 'Jetzt',
        '3d': '3 Tage',
        '7d': '7 Tage',
        '10d': '10 Tage',
        '15d': '12 Tage',
        '30d': '30 Tage',
      },
      publish: 'API',
      exeSQL: 'ExeSQL',
      exeSQLDescription:
        'Eine Komponente, die SQL-Abfragen in einer relationalen Datenbank ausführt und Abfragen von MySQL, PostgreSQL oder MariaDB unterstützt.',
      dbType: 'Datenbanktyp',
      database: 'Datenbank',
      username: 'Benutzername',
      host: 'Host',
      port: 'Port',
      password: 'Passwort',
      switch: 'Schalter',
      logicalOperator: 'Logischer Operator',
      switchOperatorOptions: {
        equal: 'Gleich',
        notEqual: 'Ungleich',
        gt: 'Größer als',
        ge: 'Größer gleich',
        lt: 'Kleiner als',
        le: 'Kleiner gleich',
        contains: 'Enthält',
        notContains: 'Enthält nicht',
        startWith: 'Beginnt mit',
        endWith: 'Endet mit',
        empty: 'Ist leer',
        notEmpty: 'Nicht leer',
      },
      switchLogicOperatorOptions: {
        and: 'UND',
        or: 'ODER',
      },
      operator: 'Operator',
      value: 'Wert',
      useTemplate: 'Diese Vorlage verwenden',
      wenCai: 'WenCai',
      queryType: 'Abfragetyp',
      wenCaiDescription:
        'Eine Komponente, die Finanzinformationen, einschließlich Aktienkursen und Finanzierungsnachrichten, von einer Vielzahl von Finanzwebsites abruft.',
      wenCaiQueryTypeOptions: {
        stock: 'Aktie',
        zhishu: 'Index',
        fund: 'Fonds',
        hkstock: 'Hongkong-Aktien',
        usstock: 'US-Aktienmarkt',
        threeboard: 'Neuer OTC-Markt',
        conbond: 'Wandelanleihe',
        insurance: 'Versicherung',
        futures: 'Futures',
        lccp: 'Finanzierung',
        foreign_exchange: 'Fremdwährung',
      },
      akShare: 'AkShare',
      akShareDescription:
        'Eine Komponente, die Nachrichten über Aktien von https://www.eastmoney.com/ abruft.',
      yahooFinance: 'YahooFinance',
      yahooFinanceDescription:
        'Eine Komponente, die Informationen über ein börsennotiertes Unternehmen anhand seines Tickersymbols abfragt.',
      crawler: 'Web-Crawler',
      crawlerDescription:
        'Eine Komponente, die HTML-Quellcode von einer angegebenen URL crawlt.',
      proxy: 'Proxy',
      crawlerResultOptions: {
        html: 'Html',
        markdown: 'Markdown',
        content: 'Inhalt',
      },
      extractType: 'Extraktionstyp',
      info: 'Info',
      history: 'Verlauf',
      financials: 'Finanzen',
      balanceSheet: 'Bilanz',
      cashFlowStatement: 'Kapitalflussrechnung',
      jin10: 'Jin10',
      jin10Description:
        'Eine Komponente, die Finanzinformationen von der Jin10 Open Platform abruft, einschließlich Nachrichtenaktualisierungen, Kalendern, Kursen und Referenzen.',
      flashType: 'Flash-Typ',
      filter: 'Filter',
      contain: 'Enthalten',
      calendarType: 'Kalendertyp',
      calendarDatashape: 'Kalender-Datenform',
      symbolsDatatype: 'Symboldatentyp',
      symbolsType: 'Symboltyp',
      jin10TypeOptions: {
        flash: 'Schnellnachrichten',
        calendar: 'Kalender',
        symbols: 'Kurse',
        news: 'Referenz',
      },
      jin10FlashTypeOptions: {
        '1': 'Marktnachrichten',
        '2': 'Futures-Nachrichten',
        '3': 'US-Hongkong-Nachrichten',
        '4': 'A-Aktien-Nachrichten',
        '5': 'Rohstoff- und Devisennachrichten',
      },
      jin10CalendarTypeOptions: {
        cj: 'Makroökonomischer Datenkalender',
        qh: 'Futures-Kalender',
        hk: 'Hongkong-Aktienmarktkalender',
        us: 'US-Aktienmarktkalender',
      },
      jin10CalendarDatashapeOptions: {
        data: 'Daten',
        event: 'Ereignis',
        holiday: 'Feiertag',
      },
      jin10SymbolsTypeOptions: {
        GOODS: 'Rohstoffkurse',
        FOREX: 'Devisenkurse',
        FUTURE: 'Internationale Marktkurse',
        CRYPTO: 'Kryptowährungskurse',
      },
      jin10SymbolsDatatypeOptions: {
        symbols: 'Rohstoffliste',
        quotes: 'Aktuelle Marktkurse',
      },
      concentrator: 'Konzentrator',
      concentratorDescription:
        'Eine Komponente, die die Ausgabe der vorgelagerten Komponente empfängt und als Eingabe an die nachgelagerten Komponenten weitergibt.',
      tuShare: 'TuShare',
      tuShareDescription:
        'Eine Komponente, die Finanznahrichten-Kurzmeldungen von führenden Finanzwebsites abruft und bei Branchen- und quantitativer Forschung hilft.',
      tuShareSrcOptions: {
        sina: 'Sina',
        wallstreetcn: 'wallstreetcn',
        '10jqka': 'Straight Flush',
        eastmoney: 'Eastmoney',
        yuncaijing: 'YUNCAIJING',
        fenghuang: 'FENGHUANG',
        jinrongjie: 'JRJ',
      },
      token: 'Token',
      src: 'Quelle',
      startDate: 'Startdatum',
      endDate: 'Enddatum',
      keyword: 'Schlüsselwort',
      note: 'Notiz',
      noteDescription: 'Notiz',
      notePlaceholder: 'Bitte geben Sie eine Notiz ein',
      invoke: 'Aufrufen',
      invokeDescription:
        'Eine Komponente, die Remote-Dienste aufrufen kann und dabei die Ausgaben anderer Komponenten oder Konstanten als Eingaben verwendet.',
      url: 'URL',
      method: 'Methode',
      timeout: 'Zeitüberschreitung',
      headers: 'Header',
      cleanHtml: 'HTML bereinigen',
      cleanHtmlTip:
        'Wenn die Antwort im HTML-Format vorliegt und nur der Hauptinhalt gewünscht wird, schalten Sie dies bitte ein.',
      reference: 'Referenz',
      input: 'Eingabe',
      output: 'Ausgabe',
      parameter: 'Parameter',
      howUseId: 'Wie verwendet man die Agenten-ID?',
      content: 'Inhalt',
      operationResults: 'Operationsergebnisse',
      autosaved: 'Automatisch gespeichert',
      optional: 'Optional',
      pasteFileLink: 'Dateilink einfügen',
      testRun: 'Testlauf',
      template: 'Vorlage',
      templateDescription:
        'Eine Komponente, die die Ausgabe anderer Komponenten formatiert. 1. Unterstützt Jinja2-Vorlagen, konvertiert zuerst die Eingabe in ein Objekt und rendert dann die Vorlage, 2. Behält gleichzeitig die ursprüngliche Methode der Verwendung von {parameter} Zeichenkettenersetzung bei',
      emailComponent: 'E-Mail',
      emailDescription: 'Sendet eine E-Mail an eine angegebene Adresse.',
      smtpServer: 'SMTP-Server',
      smtpPort: 'SMTP-Port',
      senderEmail: 'Absender-E-Mail',
      authCode: 'Autorisierungscode',
      senderName: 'Absendername',
      toEmail: 'Empfänger-E-Mail',
      ccEmail: 'CC-E-Mail',
      emailSubject: 'Betreff',
      emailContent: 'Inhalt',
      smtpServerRequired: 'Bitte geben Sie die SMTP-Serveradresse ein',
      senderEmailRequired: 'Bitte geben Sie die Absender-E-Mail ein',
      authCodeRequired: 'Bitte geben Sie den Autorisierungscode ein',
      toEmailRequired: 'Bitte geben Sie die Empfänger-E-Mail ein',
      emailContentRequired: 'Bitte geben Sie den E-Mail-Inhalt ein',
      emailSentSuccess: 'E-Mail erfolgreich gesendet',
      emailSentFailed: 'E-Mail konnte nicht gesendet werden',
      dynamicParameters: 'Dynamische Parameter',
      jsonFormatTip:
        'Die vorgelagerte Komponente sollte einen JSON-String im folgenden Format bereitstellen:',
      toEmailTip: 'to_email: Empfänger-E-Mail (Erforderlich)',
      ccEmailTip: 'cc_email: CC-E-Mail (Optional)',
      subjectTip: 'subject: E-Mail-Betreff (Optional)',
      contentTip: 'content: E-Mail-Inhalt (Optional)',
      jsonUploadTypeErrorMessage: 'Bitte laden Sie eine JSON-Datei hoch',
      jsonUploadContentErrorMessage: 'JSON-Dateifehler',
      iteration: 'Iteration',
      iterationDescription:
        'Diese Komponente teilt zunächst die Eingabe durch "Trennzeichen" in ein Array auf. Führt die gleichen Operationsschritte nacheinander für die Elemente im Array aus, bis alle Ergebnisse ausgegeben sind, was als Aufgaben-Batch-Prozessor verstanden werden kann.\n\nZum Beispiel kann innerhalb des Iterationsknotens für lange Textübersetzungen, wenn der gesamte Inhalt in den LLM-Knoten eingegeben wird, das Limit für eine einzelne Konversation erreicht werden. Der vorgelagerte Knoten kann den langen Text zuerst in mehrere Fragmente aufteilen und mit dem Iterationsknoten zusammenarbeiten, um eine Batch-Übersetzung für jedes Fragment durchzuführen, um zu vermeiden, dass das LLM-Nachrichtenlimit für eine einzelne Konversation erreicht wird.',
      delimiterTip:
        'Dieses Trennzeichen wird verwendet, um den Eingabetext in mehrere Textstücke aufzuteilen, von denen jedes als Eingabeelement jeder Iteration ausgeführt wird.',
      delimiterOptions: {
        comma: 'Komma',
        lineBreak: 'Zeilenumbruch',
        tab: 'Tabulator',
        underline: 'Unterstrich',
        diagonal: 'Schrägstrich',
        minus: 'Bindestrich',
        semicolon: 'Semikolon',
      },
      addVariable: 'Variable hinzufügen',
      variableSettings: 'Variableneinstellungen',
      globalVariables: 'Globale Variablen',
      systemPrompt: 'System-Prompt',
      addCategory: 'Kategorie hinzufügen',
      categoryName: 'Kategoriename',
      nextStep: 'Nächster Schritt',
      datatype: 'MIME-Typ der HTTP-Anfrage',
      insertVariableTip: 'Eingabe / Variablen einfügen',
      prompt: 'Prompt',
      promptTip:
        'Verwenden Sie den Systemprompt, um die Aufgabe für das LLM zu beschreiben, festzulegen, wie es antworten soll, und andere verschiedene Anforderungen zu skizzieren. Der Systemprompt wird oft in Verbindung mit Schlüsseln (Variablen) verwendet, die als verschiedene Dateninputs für das LLM dienen. Verwenden Sie einen Schrägstrich `/` oder die (x)-Schaltfläche, um die zu verwendenden Schlüssel anzuzeigen.',
      promptMessage: 'Prompt ist erforderlich',
      runningHintText: 'läuft...🕞',
    },
    footer: {
      profile: 'Alle Rechte vorbehalten @ React',
    },
    layout: {
      file: 'Datei',
      knowledge: 'Wissen',
      chat: 'Chat',
    },
  },
};
