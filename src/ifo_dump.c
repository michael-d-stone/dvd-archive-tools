#include <stdio.h>
#include <stdlib.h>

#include <dvdread/dvd_reader.h>
#include <dvdread/ifo_read.h>

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <dvd path or iso>\n", argv[0]);
        return 1;
    }

    dvd_reader_t *dvd = DVDOpen(argv[1]);
    if (!dvd) {
        fprintf(stderr, "Could not open DVD: %s\n", argv[1]);
        return 1;
    }

    ifo_handle_t *vmg = ifoOpen(dvd, 0);
    if (!vmg) {
        fprintf(stderr, "Could not open VMG IFO\n");
        DVDClose(dvd);
        return 1;
    }

    printf("Opened DVD successfully.\n");

    if (!vmg->vmgi_mat) {
        fprintf(stderr, "VMG metadata missing.\n");
        ifoClose(vmg);
        DVDClose(dvd);
        return 1;
    }

    unsigned int title_sets = vmg->vmgi_mat->vmg_nr_of_title_sets;

    printf("Title sets: %u\n", title_sets);

    if (vmg->pgci_ut) {
        printf("VMGM: has menu PGC table\n");
    } else {
        printf("VMGM: no menu PGC table\n");
    }

    for (unsigned int vts = 1; vts <= title_sets; vts++) {
        ifo_handle_t *vts_ifo = ifoOpen(dvd, vts);

        if (!vts_ifo) {
            printf("VTS %u: could not open\n", vts);
            continue;
        }

        printf("VTS %u: opened\n", vts);

        if (vts_ifo->pgci_ut) {
            printf("VTS %u: has menu PGC table\n", vts);
        } else {
            printf("VTS %u: no menu PGC table\n", vts);
        }

        ifoClose(vts_ifo);
    }

    ifoClose(vmg);
    DVDClose(dvd);

    return 0;
}
