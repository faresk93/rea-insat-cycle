/*
 * cycle.c - reconstruction of cycle.exe (INSAT CH2 2014-2015,
 * "Moyennes Cycle et Rangs", by Fares Khiary).
 *
 * Rebuilt from static disassembly of the original 32-bit MinGW binary
 * (TDM-GCC 4.7.1, SHA-256 801e1628...92d4f6). Function names, data tables,
 * strings, colours and delays come from the binary. Deviations from the
 * original are marked "DEVIATION".
 *
 * Environment (additions for testing, not in the original):
 *   CYCLE_NO_DELAY=1   skip every Sleep()/letter-by-letter delay
 *   NO_COLOR=1         disable colours (also disabled when stdout is not a tty)
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#include <io.h>
#define isatty _isatty
#define fileno _fileno
#else
#include <time.h>
#include <unistd.h>
#endif

#define NB_ETUDIANTS 74
#define TAILLE_NOM 20
#define NUMERO_SPECIAL 62 /* student who gets "Bonne Chance" instead of results */

/* conio colour numbers used by the original */
enum {
    BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, BROWN, LIGHTGRAY,
    DARKGRAY, LIGHTBLUE, LIGHTGREEN, LIGHTCYAN, LIGHTRED, LIGHTMAGENTA, YELLOW, WHITE
};

/* Tables copied byte-for-byte from the .data section of cycle.exe */

static char nom[NB_ETUDIANTS][TAILLE_NOM] = {
    " Abidi ", " Achour ", " Aidoudi ", " Ajlani ", " Athamna ",
    " Ayadi ", " Baccar ", " Baccouche ", " Baccouche ", " Baraket ",
    " Barguellil ", " Bargui ", " Barraj ", " Bel Skander ", " Ben Abdessamad ",
    " Ben Ali ", " Ben Bouzayen ", " Ben Osman ", " Ben Wannes ", " Borgini ",
    " Bouaziz ", " Boubaker ", " Brahmi ", " Brouri ", " Bzainia ",
    " Chaouch ", " Chermitti ", " Chtioui ", " Dami ", " Fennani ",
    " Gdoura ", " Ghazouani ", " Hafiene ", " Hammami ", " Hasni ",
    " Hellal ", " Jaouadi ", " Jaouadi ", " Kacem ", " Kacem ",
    " Kamoun ", " Khedhiri ", " Khiary ", " Khlifi ", " Kraiem ",
    " Kridene ", " Lahmer ", " Malouche ", " Meddeb ", " Mhadhbi ",
    " Mighri ", " Nalouti ", " Nasr ", " Nefzi ", " Rachdi ",
    " Rezgui ", " Rmili ", " Saidi ", " Sallami ", " Sayadi ",
    " Sghaier ", " Smitti ", " Soltani ", " Souissi ", " Tarhouni ",
    " Tahri ", " Teyeb ", " Trabelsi ", " Trabelsi ", " Yahmadi ",
    " Zaghouani ", " Zammel ", " Zarrouk ", " Zouari ",
};

static char prenom[NB_ETUDIANTS][TAILLE_NOM] = {
    " Mohamed", " Nadya", " Meriem", " Mahdi", " Jawaher", " Nouha",
    " Nada", " Oumayma", " Hala", " Nada", " Sana", " Emna",
    " Souad", " Sabrine", " Montassar", " Rafeh", " Abir", " Yasmine",
    " Chayma", " Ahmed", " Nouha", " Samar", " Chayma", " Rania",
    " Amir", " Feriel", " Ahmed", " Marwa", " Sabrine", " Hassen",
    " Asma", " Nizar", " Taheni", " Rawia", " Zoubeir", " Yesmine",
    " Hadhami", " Khaoula", " Fehmi", " Souha", " Amira", " Khaoula",
    " Fares", " Hiba", " Abir", " Malek", " Feten", " Nouha",
    " Yomna", " Aya", " Rimeh", " Haythem", " Emna", " Nesrine",
    " Oumeima", " Yosra", " Meriem", " Takwa", " Nour", " Sabrine",
    " Sirine", " MajdEddine", " Sinda", " Abir", " Sabri", " Marwa",
    " Marwa", " Amani", " Rayhane", " Rihab", " Taoufik", " Amal",
    " Cyrine", " Hela Beya",
};

static float moy_cba[NB_ETUDIANTS] = {
    12.06f, 12.82f, 12.19f, 11.88f, 12.06f, 12.30f, 12.79f, 12.16f, 12.22f, 12.90f,
    11.29f, 10.60f, 12.32f, 12.25f, 11.34f, 12.22f, 13.34f, 11.91f, 11.75f, 12.60f,
    12.14f, 11.88f, 13.71f, 10.78f, 11.98f, 12.32f, 13.34f, 12.29f, 12.20f, 13.06f,
    10.96f, 11.77f, 11.88f, 10.99f, 10.06f, 11.70f, 14.11f, 13.00f, 11.72f, 11.12f,
    12.20f, 14.59f, 13.60f, 12.94f, 11.87f, 13.86f, 13.71f, 12.60f, 13.32f, 14.11f,
    11.39f, 11.46f, 11.76f, 12.93f, 13.32f, 12.29f, 12.69f, 13.97f, 12.40f, 12.45f,
    12.66f, 10.78f, 13.94f, 11.54f, 12.28f, 12.77f, 12.20f, 12.68f, 11.85f, 11.27f,
    11.77f, 13.14f, 11.75f, 11.75f,
};

static float moy_ch2[NB_ETUDIANTS] = {
    11.11f, 12.01f, 12.29f, 10.36f, 12.98f, 10.90f, 12.56f, 11.63f, 11.70f, 11.09f,
    11.16f, 11.14f, 12.08f, 10.31f, 10.56f, 11.11f, 12.12f, 11.66f, 10.59f, 11.79f,
    10.76f, 10.37f, 11.66f, 10.74f, 10.30f, 11.56f, 12.63f, 11.96f, 10.42f, 11.95f,
    12.50f, 12.43f, 11.32f, 10.71f, 10.87f, 10.69f, 12.92f, 12.84f, 11.07f, 12.96f,
    10.41f, 14.49f, 11.90f, 11.35f, 11.03f, 12.51f, 11.83f, 12.24f, 11.23f, 12.35f,
    11.24f, 8.81f, 12.09f, 12.50f, 10.62f, 11.01f, 12.06f, 13.93f, 13.63f, 12.61f,
    11.27f, 2.30f, 13.79f, 11.61f, 10.23f, 11.43f, 11.39f, 11.23f, 10.13f, 10.83f,
    12.67f, 11.75f, 10.70f, 11.90f,
};

/* ---------------------------------------------------------------------------
 * Console layer (stands in for the conio2 library linked into the original)
 * ------------------------------------------------------------------------- */

static int couleurs_actives = -1;
static int sans_delai = -1;
static int couleur_texte = LIGHTGRAY;
static int couleur_fond = BLACK;

static int utiliser_couleurs(void)
{
    if (couleurs_actives < 0)
        couleurs_actives = getenv("NO_COLOR") == NULL && isatty(fileno(stdout));
    return couleurs_actives;
}

static void appliquer_couleurs(void)
{
    if (!utiliser_couleurs())
        return;
    fflush(stdout);
#ifdef _WIN32
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE),
                            (WORD)((couleur_fond << 4) | couleur_texte));
#else
    {
        /* conio order is BGR, ANSI order is RGB */
        static const int ansi[8] = {0, 4, 2, 6, 1, 5, 3, 7};
        int fg = ansi[couleur_texte & 7] + (couleur_texte & 8 ? 90 : 30);
        int bg = ansi[couleur_fond & 7] + (couleur_fond & 8 ? 100 : 40);
        printf("\033[%d;%dm", fg, bg);
    }
#endif
}

static void textcolor(int c)
{
    couleur_texte = c & 15;
    appliquer_couleurs();
}

static void textbackground(int c)
{
    couleur_fond = c & 15;
    appliquer_couleurs();
}

static void restaurer_console(void)
{
    if (!utiliser_couleurs())
        return;
#ifdef _WIN32
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), LIGHTGRAY);
#else
    printf("\033[0m");
#endif
    fflush(stdout);
}

static void attendre(unsigned ms)
{
    if (sans_delai < 0)
        sans_delai = getenv("CYCLE_NO_DELAY") != NULL;
    fflush(stdout);
    if (sans_delai)
        return;
#ifdef _WIN32
    Sleep(ms);
#else
    {
        struct timespec t = {ms / 1000, (long)(ms % 1000) * 1000000L};
        nanosleep(&t, NULL);
    }
#endif
}

/* ---------------------------------------------------------------------------
 * Display helpers (original names)
 * ------------------------------------------------------------------------- */

/* Pads with spaces so that s ends up centred on an 80-column console. */
static void center(const char *s)
{
    printf("%*s", 40 - (int)(strlen(s) >> 1), " ");
}

/* Types s one character at a time, ms milliseconds per character. */
static void letter(const char *s, unsigned ms)
{
    size_t i;
    for (i = 0; i < strlen(s); i++) {
        putchar(s[i]); /* original: _cprintf("%c", s[i]) */
        attendre(ms);
    }
}

static void letterc(const char *s, unsigned ms)
{
    center(s);
    letter(s, ms);
}

static void reculer(const char *s)
{
    size_t i;
    for (i = 0; i < strlen(s); i++)
        putchar('\b');
}

/* Prints s n times alternating colours c1/c2, overwriting itself. */
static void blink1(const char *s, int c1, int c2, int n, const char *mode)
{
    int premier = 1;
    int i;

    if (strcmp(mode, "Center") == 0)
        center(s);
    for (i = 1; i <= n; i++) {
        if (!premier)
            reculer(s);
        textcolor(c1);
        printf("%s", s);
        attendre(550);
        reculer(s);
        textcolor(c2);
        printf("%s", s);
        attendre(550);
        premier = 0;
    }
}

/* Like blink1 but types the text with letter(). The original never clears
 * its "first pass" flag, so it always ends with the cursor rewound. */
static void blink2(const char *s, int c1, int c2, int n, const char *mode)
{
    int i;

    if (strcmp(mode, "Center") == 0)
        center(s);
    for (i = 1; i <= n; i++) {
        textcolor(c1);
        letter(s, 30);
        attendre(50);
        reculer(s);
        textcolor(c2);
        letter(s, 30);
        attendre(50);
        reculer(s);
    }
}

/* Alternates s between white-on-black and black-on-white n times. */
static void blink3(const char *s, int n, const char *mode)
{
    int i;

    if (strcmp(mode, "Center") == 0)
        center(s);
    for (i = 1; i <= n; i++) {
        textcolor(WHITE);
        textbackground(BLACK);
        printf("%s", s);
        attendre(600);
        reculer(s);
        textcolor(BLACK);
        textbackground(WHITE);
        printf("%s", s);
        attendre(600);
        reculer(s);
    }
}

/* "Thinking" dots before a verdict. */
static void point(void)
{
    int i;

    attendre(800);
    for (i = 0; i < 4; i++) {
        printf("\n .");
        if (i < 3)
            attendre(600);
    }
    printf("\n\n ");
    attendre(1000);
}

/* ---------------------------------------------------------------------------
 * Ranking
 * ------------------------------------------------------------------------- */

/* Number of entries equal to v. */
static int Occurences(const float t[NB_ETUDIANTS], float v)
{
    int n = 0;
    int i;
    for (i = 0; i < NB_ETUDIANTS; i++)
        if (t[i] == v)
            n++;
    return n;
}

/* Ascending bubble sort, in place. */
static void tri(float t[NB_ETUDIANTS])
{
    int i, j;
    for (i = NB_ETUDIANTS; i != 0; i--)
        for (j = 0; j < i - 1; j++)
            if (t[j] > t[j + 1]) {
                float x = t[j];
                t[j] = t[j + 1];
                t[j + 1] = x;
            }
}

/*
 * Competition rank of v in t (1 = best, ties share a rank). Sorts t in place
 * and fills rangs[] with the rank of each position, best first.
 *
 * DEVIATION: at i == 0 the original also compares t[0] with t[-1], one float
 * before the array. Here that comparison is treated as "not equal", which is
 * what the original does unless that stray stack value happens to match.
 * DEVIATION: the original returns an uninitialised value when v is absent;
 * this returns 0. Neither case occurs with the built-in tables.
 */
static int rang(float t[NB_ETUDIANTS], int rangs[NB_ETUDIANTS + 1], float v)
{
    int k = 0;
    int r = 1;
    int i;

    tri(t);
    for (i = NB_ETUDIANTS - 1; i >= 0; i--) {
        if (i > 0 && t[i] == t[i - 1]) {
            rangs[k] = r;
            rangs[k + 1] = r;
        } else {
            rangs[k] = r;
            r += Occurences(t, t[i]);
        }
        k++;
    }
    for (i = 0; i < NB_ETUDIANTS; i++)
        if (t[i] == v)
            return rangs[NB_ETUDIANTS - 1 - i];
    return 0;
}

/* ---------------------------------------------------------------------------
 * Verdict messages
 * ------------------------------------------------------------------------- */

/* Bands are tenths of the class: 7.4 = 10% of 74 students. */
#define DANS(r, bas, haut) ((r) > (bas) && (r) <= (haut))

static void marge_cba(int r)
{
    textcolor(WHITE);
    if (r == 1)
        letter("\n Vous avez eu la meilleure Moyenne CBA !", 30);
    else if (r <= 7)
        letter("\n Vous avez ete parmi 10% des meilleures Moyennes CBA.", 30);
    else if (DANS(r, 7.4, 14.8))
        letter("\n Vous avez ete parmi 20% des meilleures Moyennes CBA.", 30);
    else if (DANS(r, 14.8, 22.2))
        letter("\n Vous avez ete parmi 30% des meilleures Moyennes CBA.", 30);
    else if (DANS(r, 22.2, 29.6))
        letter("\n Vous avez ete parmi 40% des meilleures Moyennes CBA.", 30);
    else if (DANS(r, 29.6, 37.0))
        letter("\n Vous avez ete parmi 50% des meilleures Moyennes CBA.", 30);
    else if (r > 37)
        letter("\n Vous avez ete parmi la 2eme 50% des meilleures Moyennes CBA.", 30);
    putchar('\n');
}

static void marge_ch2(int r, int numero)
{
    textcolor(WHITE);
    if (r == 1) {
        letter("\n Felicitations", 30);
        textcolor(LIGHTCYAN);
        textbackground(BLACK);
        letter(prenom[numero - 1], 30);
        textcolor(WHITE);
        letter(" ! Vous avez la meilleure Moyenne CH2.", 30);
    } else if (r <= 7.4)
        letter("\n Vous etes parmi 10% des meilleures Moyennes CH2.", 30);
    else if (DANS(r, 7.4, 14.8))
        letter("\n Vous etes parmi 20% des meilleures Moyennes CH2.", 30);
    else if (DANS(r, 14.8, 22.2))
        letter("\n Vous etes parmi 30% des meilleures Moyennes CH2.", 30);
    else if (DANS(r, 22.2, 29.6))
        letter("\n Vous etes parmi 40% des meilleures Moyennes CH2.", 30);
    else if (DANS(r, 29.6, 37.0))
        letter("\n Vous etes parmi 50% des meilleures Moyennes CH2.", 30);
    else if (r > 37)
        letter("\n Vous etes parmi la 2eme 50% des meilleures Moyennes CH2.", 30);
    putchar('\n');
}

/* "Felicitations <prenom> ----> in sha'ALLAH  Passage Garanti" */
static void passage_garanti(int numero, int clignotements)
{
    point();
    letter(" Felicitations", 50);
    textcolor(LIGHTCYAN);
    textbackground(BLACK);
    letter(prenom[numero - 1], 30);
    textcolor(WHITE);
    attendre(800);
    letter(" ----> ", 60);
    attendre(400);
    letter("in sha'ALLAH ", 60);
    attendre(300);
    textcolor(GREEN);
    textbackground(LIGHTGREEN);
    blink1(" Passage Garanti ", WHITE, BLACK, clignotements, " ");
    textcolor(WHITE);
    textbackground(BLACK);
}

static void marge_cycle(int r, int numero)
{
    static const struct {
        double bas, haut;
        const char *message;
    } bandes[] = {
        {7.4, 14.8, "\n Vous etes parmi 20% des meilleures Moyennes Cycle Ingenieur."},
        {14.8, 22.2, "\n Vous etes parmi 30% des meilleures Moyennes Cycle Ingenieur."},
        {22.2, 29.6, "\n Vous etes parmi 40% des meilleures Moyennes Cycle Ingenieur."},
        {29.6, 37.0, "\n Vous etes parmi 50% des meilleures Moyennes Cycle Ingenieur."},
        {37.0, 44.4, "\n Vous etes parmi 60% des meilleures Moyennes Cycle Ingenieur."},
    };
    size_t b;

    textcolor(WHITE);
    if (r == 1) {
        letter("\n Felicitations", 30);
        textcolor(LIGHTCYAN);
        textbackground(BLACK);
        letter(prenom[numero - 1], 30);
        textcolor(WHITE);
        letter(" ! Vous avez la meilleure Moyenne Cycle Ingenieur.", 30);
        point();
        letter(" Felicitations encore", 30);
        textcolor(LIGHTCYAN);
        textbackground(BLACK);
        letter(prenom[numero - 1], 30);
        textcolor(WHITE);
        attendre(800);
        attendre(800);
        letter(" ----> ", 60);
        attendre(400);
        letter("in sha'ALLAH ", 60);
        attendre(300);
        textcolor(GREEN);
        textbackground(LIGHTGREEN);
        blink1(" Passage Garanti ", WHITE, BLACK, 6, " ");
        textcolor(WHITE);
        textbackground(BLACK);
    } else if (r <= 7.4) {
        letter("\n Vous etes parmi 10% des meilleures Moyennes Cycle Ingenieur.", 30);
        passage_garanti(numero, 6);
    } else {
        for (b = 0; b < sizeof bandes / sizeof bandes[0]; b++)
            if (DANS(r, bandes[b].bas, bandes[b].haut)) {
                letter(bandes[b].message, 30);
                passage_garanti(numero, 6);
                if (b == 0) /* only the 20% band ends with a newline */
                    putchar('\n');
                break;
            }
        if (b == sizeof bandes / sizeof bandes[0]) {
            if (r <= 52 && r > 44.4) {
                letter("\n Vous etes parmi les 52 Meilleures Moyennes Cycle Ingenieur.", 30);
                passage_garanti(numero, 3);
            } else if (r > 52) {
                point();
                letter(" Desole", 50);
                textcolor(LIGHTCYAN);
                textbackground(BLACK);
                letter(prenom[numero - 1], 30);
                attendre(1000);
                textcolor(RED);
                textbackground(BLACK);
                letter(" Vous etes parmi les 21 dernieres Moyennes Cycle Ingenieur.", 50);
            }
        }
    }
    textcolor(BLACK);
}

/* ---------------------------------------------------------------------------
 * Averages
 * ------------------------------------------------------------------------- */

/*
 * Moyenne Cycle = (CBA + 2 x CH2) / 3 with a 0.5 bonus on each part, except
 * for students the original hard-codes (0-based indices). Those cases look
 * like resit averages, but the binary only shows the arithmetic.
 */
static float moyenne_cycle(int i, float cba, float ch2)
{
    double t;

    switch (i) {
    case 34:
        t = (ch2 + 9.68) / 2.0 - 0.5;
        return (float)(((cba + 0.5) + (t + t)) / 3.0);
    case 51:
        return (float)(((cba + 9.89) / 2.0 - 0.5 + 19.38) / 3.0);
    case 69:
        return (float)(((cba + 9.47) / 2.0 - 0.5 + 21.66) / 3.0);
    case 3:
    case 11:
    case 33:
    case 68:
        return (float)(((cba + 0.5) + (ch2 + (double)ch2)) / 3.0);
    default:
        t = ch2 + 0.5;
        return (float)(((cba + 0.5) + (t + t)) / 3.0);
    }
}

/* ---------------------------------------------------------------------------
 * Results (a GCC nested function inside main in the original)
 * ------------------------------------------------------------------------- */

struct etudiant {
    int numero; /* 1..74 as typed */
    float moy_cba, moy_ch2, moy_cycle;
    int rang_cba, rang_ch2, rang_cycle;
    char r_cba[10], r_ch2[10], r_cycle[10]; /* "-N/74-" */
    char nom_complet[2 * TAILLE_NOM];
};

static void resultat(const struct etudiant *e)
{
    puts("\n");
    textcolor(BLACK);
    textbackground(BLACK);
    blink3(e->nom_complet, 3, "Center");
    puts("\n");
    attendre(1000);

    textcolor(LIGHTGREEN);
    textbackground(BLACK);
    letter("\n-Moyenne CBA   : ", 30);
    textcolor(WHITE);
    printf("%.2f", e->moy_cba);
    textcolor(GREEN);
    attendre(700);
    letter("  | Rang CBA   ", 30);
    textcolor(LIGHTGREEN);
    printf(": ");
    textbackground(GREEN);
    textcolor(BLACK);
    blink1(e->r_cba, BLACK, WHITE, 2, " ");
    textbackground(BLACK);
    marge_cba(e->rang_cba);
    attendre(500);

    textcolor(LIGHTRED);
    attendre(500);
    letter("\n-Moyenne CH2   : ", 30);
    textcolor(WHITE);
    printf("%.2f", e->moy_ch2);
    textcolor(RED);
    attendre(700);
    letter("  | Rang CH2   ", 30);
    textcolor(LIGHTRED);
    printf(": ");
    textbackground(RED);
    textcolor(BLACK);
    blink1(e->r_ch2, BLACK, WHITE, 2, " ");
    textbackground(BLACK);
    marge_ch2(e->rang_ch2, e->numero);
    attendre(500);

    puts("\n");
    attendre(1000);
    textcolor(LIGHTMAGENTA);
    letter("-Moyenne Cycle : ", 30);
    textcolor(WHITE);
    printf("%.3f", e->moy_cycle);
    textcolor(MAGENTA);
    attendre(1000);
    letter(" | Rang Cycle ", 30);
    textcolor(LIGHTMAGENTA);
    printf(": ");
    textbackground(MAGENTA);
    textcolor(BLACK);
    blink1(e->r_cycle, BLACK, WHITE, 2, " ");
    textbackground(BLACK);
    marge_cycle(e->rang_cycle, e->numero);
    attendre(800);
}

/* ---------------------------------------------------------------------------
 * main
 * ------------------------------------------------------------------------- */

static void entete(void)
{
    putchar('\n');
    textcolor(GREEN);
    letterc("* Au nom d'ALLAH *\n", 40);
    attendre(500);
    letterc("** le Tout Misericordieux, le Tres Misericordieux **", 40);
    puts("\n");
    attendre(700);
    textcolor(RED);
    textbackground(BLACK);
    letterc("-I.N.S.A.T-\n", 30);
    attendre(400);
    textcolor(MAGENTA);
    textbackground(BLACK);
    letterc("-CH2 |2014-2015|-\n\n", 30);
    attendre(600);
    textcolor(LIGHTRED);
    textbackground(BLACK);
    blink1("-\\_Moyennes Cycle et Rangs_/-", RED, LIGHTRED, 3, "Center");
    textcolor(WHITE);
    puts("\n");
    textcolor(LIGHTGRAY);
    blink2("-Fares Khiary-", DARKGRAY, LIGHTGRAY, 2, "Center");
    putchar('\n');
    letterc("--------------", 5);
    puts("\n");
    attendre(600);
    textcolor(WHITE);
    textbackground(BLACK);
}

/* DEVIATION: the original loops forever on non-numeric input or EOF.
 * Returns 0 at end of input. */
static int lire_numero(void)
{
    int n = 0;
    int lu;

    do {
        lu = scanf("%d", &n);
        if (lu == EOF)
            return 0;
        if (lu == 0) {
            if (scanf("%*s") == EOF)
                return 0;
            n = 0;
        }
    } while (n <= 0 || n > NB_ETUDIANTS);
    return n;
}

/* Returns 1 to start again. DEVIATION: returns 0 at end of input. */
static int recommencer(void)
{
    char c;

    textcolor(WHITE);
    puts("\n\n");
    attendre(2000);
    letter("Recommencer ?", 30);
    attendre(500);
    letter("\nOui : O", 30);
    letter("\nNon : N     ", 30);
    do {
        if (scanf("%c", &c) != 1)
            return 0;
    } while (c != 'o' && c != 'O' && c != 'n' && c != 'N');
    return c == 'o' || c == 'O';
}

int main(void)
{
    float cba[NB_ETUDIANTS], ch2[NB_ETUDIANTS], cyc[NB_ETUDIANTS];
    int rangs_cba[NB_ETUDIANTS + 1], rangs_ch2[NB_ETUDIANTS + 1], rangs_cyc[NB_ETUDIANTS + 1];
    int continuer = 1;
    int i;

    entete();
    while (continuer) {
        struct etudiant e;

        /* rang() sorts its array, so start from fresh copies every round */
        memcpy(cba, moy_cba, sizeof cba);
        memcpy(ch2, moy_ch2, sizeof ch2);
        for (i = 0; i < NB_ETUDIANTS; i++)
            cyc[i] = moyenne_cycle(i, cba[i], ch2[i]);

        textcolor(WHITE);
        puts("\n\n");
        attendre(1000);
        letter(" Veuillez saisir votre nombre : ", 30);
        textcolor(WHITE);
        e.numero = lire_numero();
        if (e.numero == 0)
            break;

        e.moy_cba = cba[e.numero - 1];
        e.moy_ch2 = ch2[e.numero - 1];
        e.moy_cycle = cyc[e.numero - 1];
        e.rang_cba = rang(cba, rangs_cba, e.moy_cba);
        sprintf(e.r_cba, "-%d/74-", e.rang_cba);
        e.rang_ch2 = rang(ch2, rangs_ch2, e.moy_ch2);
        sprintf(e.r_ch2, "-%d/74-", e.rang_ch2);
        e.rang_cycle = rang(cyc, rangs_cyc, e.moy_cycle);
        sprintf(e.r_cycle, "-%d/74-", e.rang_cycle);
        strcpy(e.nom_complet, prenom[e.numero - 1]);
        strcat(e.nom_complet, nom[e.numero - 1]);

        if (e.numero == NUMERO_SPECIAL) {
            letter("\n\nBonne Chance pour l'annee prochaine", 30);
            textcolor(LIGHTCYAN);
            letter(prenom[NUMERO_SPECIAL - 1], 30);
            textcolor(BLACK);
            attendre(500);
        } else {
            resultat(&e);
        }
        continuer = recommencer();
    }

    printf("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
           "                                          ");
    letter("Programme par : ", 30);
    attendre(500);
    textcolor(DARKGRAY);
    blink2("-Fares Khiary-", DARKGRAY, LIGHTGRAY, 3, " ");
    blink3("-Fares Khiary-", 1, " ");
    textbackground(BLACK);
    printf("\n\n                                          ");
    attendre(1000);
    textcolor(WHITE);
    letter("Peace !\n\n", 30);
    attendre(1000);
    restaurer_console();
#ifdef _WIN32
    system("pause");
#endif
    return 0;
}
