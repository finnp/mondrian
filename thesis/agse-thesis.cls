\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{agse-thesis}[2017/05/23 v0.1 AGSE Thesis]

%%% Read options
% Language: Default is German
\newcommand{\lang}{ngerman}
\DeclareOption{de}{\renewcommand{\lang}{ngerman}}
\DeclareOption{en}{\renewcommand{\lang}{english}}

% Font family: Default is LaTeX's lmodern
\newcommand{\fonttype}{plain}
\DeclareOption{serif}{     \renewcommand{\fonttype}{serif}}
\DeclareOption{plain}{     \renewcommand{\fonttype}{plain}}
\DeclareOption{sans-serif}{\renewcommand{\fonttype}{sans-serif}}

% Document type: Default is article (twosided)
\newcommand{\baseClass}{article}
\DeclareOption{article}{%
    \renewcommand{\baseClass}{article}
    \PassOptionsToClass{twoside}{article}
}
\DeclareOption{book}{\renewcommand{\baseClass}{book}}

\newcommand{\useparskip}{no}
\DeclareOption{parskip}{\renewcommand{\useparskip}{yes}}
\DeclareOption{noparskip}{\renewcommand{\useparskip}{no}}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\baseClass}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{\baseClass}

% Load required language
\RequirePackage[\lang]{babel}

% Load required font
\RequirePackage{xifthen}
\ifthenelse{\equal{\fonttype}{plain}}{
    \RequirePackage{lmodern}
}{}
\ifthenelse{\equal{\fonttype}{serif}}{
    \RequirePackage[sc]{mathpazo}
    \linespread{1.05}  % Palladio needs more leading (space between lines)
}{}
\ifthenelse{\equal{\fonttype}{sans-serif}}{
    \RequirePackage{paratype}
    \renewcommand*\familydefault{\sfdefault}
}{}
\RequirePackage[T1]{fontenc}

% Allow unicode in input files
\RequirePackage[utf8]{inputenc}

% Set layout
\RequirePackage[
    inner=3.4cm,
    outer=3cm,
    top=3cm,
    marginparwidth=2.5cm,
    marginparsep=0.1cm
]{geometry}

\ifthenelse{\equal{\useparskip}{yes}}{
    \RequirePackage{parskip}
}{}

% Header and Footer Style
\RequirePackage{fancyhdr}
\pagestyle{fancy}
\fancyhead{}
\fancyhead[OR]{\slshape\nouppercase{\rightmark}}
\fancyhead[EL]{\slshape\nouppercase{\leftmark}}
\fancyfoot{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}

% Display Chapter and Section for book class
\ifthenelse{\equal{\baseClass}{book}}{
    \renewcommand{\chaptermark}[1]{\markboth{%
        \chaptername\ \thechapter.\ #1}{\chaptername\ \thechapter.\ #1}}
}{%
% Display Section and Subsection for article class
    \renewcommand{\sectionmark}[1]{\markboth{%
        \thesection.\ #1}{\thesection.\ #1}}
}

% PDF settings
\usepackage[%
    pdfstartview=FitH,
    linktocpage,
% two lines below = color links
    colorlinks=true,
    citecolor=blue!20!black!30!green,
% two lines below = don't color links
    %colorlinks=false,
    %pdfborder={0 0 0},
]{hyperref}

% Tables
\usepackage{tabularx}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}

% Misc
\RequirePackage{fancyref}
\RequirePackage{url}
\RequirePackage{makeidx}

\RequirePackage[pdftex]{graphicx}

%%% BibTeX
\RequirePackage[numbers,sort&compress]{natbib}
\RequirePackage[nottoc]{tocbibind}
\bibliographystyle{plain}

% Java Code Listing Style
\RequirePackage{xcolor}
\RequirePackage{listings}
\definecolor{darkblue}{rgb}{0,0,.6}
\definecolor{darkgreen}{rgb}{0,0.5,0}
\definecolor{darkred}{rgb}{0.5,0,0}
\lstset{%
    language=Java,
    basicstyle=\ttfamily\small\upshape,
    commentstyle=\color{darkgreen}\sffamily,
    keywordstyle=\color{darkblue}\rmfamily\bfseries,
    breaklines=true,
    tabsize=2,
    xleftmargin=3mm,
    xrightmargin=3mm,
    numbers=none,
    frame=single,
    stringstyle=\color{darkred},
    showstringspaces=false
}

% Custom commands
\newcommand\zb{z.\,B.\ }
\renewcommand\dh{d.\,h.\ }
\newcommand{\mailto}[1]{\href{mailto:#1}{#1}}

\RequirePackage{pgfkeys}
\pgfkeys{
    student/id/.estore in = \studentID,
    student/mail/.estore in = \coverpageMail,
    thesis/type/.estore in = \thesisType,
    thesis/type = Bachelorarbeit,
    thesis/date/.estore in = \thesisDate,
    thesis/date = \today,
    thesis/advisor/.estore in = \advisor,
    thesis/examiner/.estore in = \firstExaminer,
    thesis/examiner/2/.estore in = \secondExaminer,
    thesis/group/.estore in = \groupName,
    thesis/group = {Arbeitsgruppe Software Engineering},
    title/size/.store in = \titleFontSize,
    abstract/separate/.estore in = \separateAbstract,
}

% Define abstract environment for book class
\ifthenelse{\equal{\baseClass}{book}}%
    {\newenvironment{abstract}%
        {\begin{center}\textbf{\small\abstractname}\end{center}\quotation\small}%
        {\endquotation}%
    }{}

% (Re)define frontmatter and mainmatter
\ifthenelse{\equal{\baseClass}{book}}{
    \let\frontmatterOrig\frontmatter
    \renewcommand{\frontmatter}{
        \frontmatterOrig
        \pagestyle{plain}
    }
    \let\mainmatterOrig\mainmatter
    \renewcommand{\mainmatter}{
        \mainmatterOrig
        \pagestyle{fancy}
        \setcounter{page}{1}
    }
}{
    \newcommand{\frontmatter}{
        \pagestyle{plain}
        \pagenumbering{roman}
        \setcounter{page}{1}
    }
    \newcommand{\mainmatter}{
        \pagestyle{fancy}
        \pagenumbering{arabic}
        \setcounter{page}{1}
    }
}

\RequirePackage{xstring}
\RequirePackage{etoolbox}
\newcommand{\coverpage}[2][]{
    \pgfkeys{#1}
    \pagestyle{empty}

    \ifcsdef{separateAbstract}{\mbox{}\vspace{15mm}}{\mbox{}}

    \begin{center}
        \LARGE
        \textbf{Freie Universität Berlin}

        \vspace{4mm}

        \normalsize
        \thesisType{} am Institut für Informatik der Freien Universität Berlin

        \vspace{2mm}

        \groupName

        \ifcsdef{separateAbstract}{\vspace{25mm}}{\vspace{13mm}}

        \ifcsdef{titleFontSize}{}{%
            \StrLen{\thesisTitle}[\titleLength]
            \ifthenelse{\titleLength > 100}{%
                \let\titleFontSize\LARGE
            }{%
                \let\titleFontSize\huge
            }
        }
        \titleFontSize\thesisTitle

        \ifcsdef{separateAbstract}{\vfill}{\vspace{13mm}}

        \Large
        \studentName \\
        \normalsize
        Matrikelnummer: \studentID\\
        \mailto{\coverpageMail}

        \vspace{4mm}

        \begin{tabular}{rl}
            \ifcsdef{advisor}{Betreuer: & \advisor\\}{}
            Eingereicht bei: & \firstExaminer \\
            \ifcsdef{secondExaminer}{Zweitgutachter: & \secondExaminer\\}{}
        \end{tabular}

        \vspace{4mm}

        Berlin, \thesisDate
    \end{center}

    \ifcsdef{separateAbstract}{\cleardoublepage\frontmatter}{\vfill}
    \begin{abstract}
        #2
    \end{abstract}
    \cleardoublepage
    \ifcsdef{separateAbstract}{}{\frontmatter}
}
