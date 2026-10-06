/* Headless real mGBA core execution. No save file or external BIOS is loaded.
 * Input route on stdin: frame_count key_mask screenshot_name (or -).
 * GBA keys: A=1, B=2, Select=4, Start=8, Right=16, Left=32, Up=64, Down=128.
 * Screenshots are PPM, deliberately separate from behavioral acceptance. */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/version.h>
#include <mgba/core/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void emulator_log(struct mLogger *logger, int category, enum mLogLevel level,
                         const char *format, va_list args)
{
    (void)logger;
    fprintf(stderr, "%s [%d]: ", mLogCategoryName(category), level);
    vfprintf(stderr, format, args);
    fputc('\n', stderr);
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: boot-baseline ROM < route.txt\n"); return 2; }
    struct mLogger logger = { .log = emulator_log, .filter = NULL };
    mLogSetDefaultLogger(&logger);
    struct mCore *core = mCoreFind(argv[1]);
    if (!core || !core->init(core)) return 3;
    mCoreConfigInit(&core->config, NULL);
    unsigned width, height;
    core->desiredVideoDimensions(core, &width, &height);
    color_t *pixels = calloc(width * height, sizeof(*pixels));
    if (!pixels) return 4;
    core->setVideoBuffer(core, pixels, width);
    core->setAudioBufferSize(core, 1024);
    if (!mCoreLoadFile(core, argv[1])) return 5;
    core->reset(core);
    printf("mGBA %s; %ux%u; fresh save; built-in BIOS\n", projectVersion, width, height);
    unsigned frames, keys, total = 0;
    char name[128];
    while (scanf("%u %u %127s", &frames, &keys, name) == 3) {
        if (frames > 36000 || keys > 1023) return 6;
        core->setKeys(core, keys);
        for (unsigned i = 0; i < frames; ++i) core->runFrame(core);
        total += frames;
        printf("frame=%u keys=%u capture=%s\n", total, keys, name);
        if (strcmp(name, "-") != 0) {
            FILE *file = fopen(name, "wb");
            if (!file) return 7;
            fprintf(file, "P6\n%u %u\n255\n", width, height);
            for (unsigned i = 0; i < width * height; ++i) {
                unsigned char rgb[] = {pixels[i] & 255, (pixels[i] >> 8) & 255, (pixels[i] >> 16) & 255};
                if (fwrite(rgb, 1, 3, file) != 3) return 8;
            }
            if (fclose(file)) return 9;
        }
    }
    mCoreConfigDeinit(&core->config);
    core->deinit(core);
    mLogSetDefaultLogger(NULL);
    free(pixels);
    return 0;
}
