#include <stdio.h>
#include <stdlib.h>

#include <dvdread/dvd_reader.h>
#include <dvdread/ifo_read.h>

static void print_menu_pgcs(const char *domain, pgci_ut_t *pgci_ut)
{
    if (!pgci_ut) {
        printf("%s: no menu PGC table\n", domain);
        return;
    }

    printf("%s: %u language unit(s)\n",
           domain,
           pgci_ut->nr_of_lus);

    for (unsigned int lu_index = 0;
         lu_index < pgci_ut->nr_of_lus;
         lu_index++) {

        pgci_lu_t *lu = &pgci_ut->lu[lu_index];

        unsigned char lang1 = (lu->lang_code >> 8) & 0xff;
        unsigned char lang2 = lu->lang_code & 0xff;

        printf("  LU %u: language=%c%c exists=0x%02x\n",
               lu_index + 1,
               lang1 ? lang1 : '?',
               lang2 ? lang2 : '?',
               lu->exists);

        if (!lu->pgcit) {
            printf("    no PGC table\n");
            continue;
        }

        printf("    PGC count: %u\n",
               lu->pgcit->nr_of_pgci_srp);

        for (unsigned int pgc_index = 0;
             pgc_index < lu->pgcit->nr_of_pgci_srp;
             pgc_index++) {

            pgci_srp_t *srp =
                &lu->pgcit->pgci_srp[pgc_index];

            pgc_t *pgc = srp->pgc;

            unsigned int pgc_number = pgc_index + 1;

            if (!pgc) {
                printf("      PGC %u: no PGC data\n",
                       pgc_number);
                continue;
            }

            int ffmpeg_candidate =
                pgc->nr_of_programs > 0 &&
                pgc->nr_of_cells > 0 &&
                pgc->program_map != NULL &&
                pgc->cell_playback != NULL;

            printf(
                "      PGC %u: programs=%u cells=%u "
                "program_map=%s cell_playback=%s %s\n",
                pgc_number,
                pgc->nr_of_programs,
                pgc->nr_of_cells,
                pgc->program_map ? "yes" : "no",
                pgc->cell_playback ? "yes" : "no",
                ffmpeg_candidate
                    ? "[ffmpeg candidate]"
                    : "[not playable]"
            );
        }
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr,
                "Usage: %s <dvd path or iso>\n",
                argv[0]);
        return 1;
    }

    dvd_reader_t *dvd = DVDOpen(argv[1]);

    if (!dvd) {
        fprintf(stderr,
                "Could not open DVD: %s\n",
                argv[1]);
        return 1;
    }

    ifo_handle_t *vmg = ifoOpen(dvd, 0);

    if (!vmg) {
        fprintf(stderr,
                "Could not open VMG IFO\n");
        DVDClose(dvd);
        return 1;
    }

    printf("Opened DVD successfully.\n");

    if (!vmg->vmgi_mat) {
        fprintf(stderr,
                "VMG metadata missing.\n");
        ifoClose(vmg);
        DVDClose(dvd);
        return 1;
    }

    unsigned int title_sets =
        vmg->vmgi_mat->vmg_nr_of_title_sets;

    printf("Title sets: %u\n\n", title_sets);

    print_menu_pgcs("VMGM", vmg->pgci_ut);

    printf("\n");

    for (unsigned int vts = 1;
         vts <= title_sets;
         vts++) {

        ifo_handle_t *vts_ifo =
            ifoOpen(dvd, vts);

        if (!vts_ifo) {
            printf("VTS %u: could not open\n\n", vts);
            continue;
        }

        char domain[32];

        snprintf(domain,
                 sizeof(domain),
                 "VTSM VTS=%u",
                 vts);

        print_menu_pgcs(domain,
                        vts_ifo->pgci_ut);

        printf("\n");

        ifoClose(vts_ifo);
    }

    ifoClose(vmg);
    DVDClose(dvd);

    return 0;
}
