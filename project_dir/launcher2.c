#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024
#define MAX_PATH_LEN 1024

int main() {
    char config_path[] = "config.txt";
    char VENV_PATH[MAX_PATH_LEN] = {0};

    FILE *f = fopen(config_path, "r");
    if (!f) {
        fprintf(stderr, "Failed to open config file: %s\n", config_path);
        return 1;
    }

    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        // Strip newline characters
        line[strcspn(line, "\r\n")] = 0;

        // Look for VENV_PATH= in the line
        char *eq = strstr(line, "VENV_PATH=");
        if (eq) {
            char *val = eq + strlen("VENV_PATH=");
            if (*val != '\0') {
                // Copy the value into VENV_PATH
                strncpy(VENV_PATH, val, MAX_PATH_LEN - 1);
                VENV_PATH[MAX_PATH_LEN - 1] = '\0'; // safety
                printf("Found VENV_PATH: %s\n", VENV_PATH);
            } else {
                fprintf(stderr, "No path provided for VENV_PATH in config\n");
                fclose(f);
                return 1;
            }
        }
    }

    fclose(f);

    if (strlen(VENV_PATH) == 0) {
        fprintf(stderr, "VENV_PATH not found in config\n");
        return 1;
    }

    // Build the system command dynamically
    char cmd[2048];
    snprintf(cmd, sizeof(cmd),
             "runtime\\usr\\bin\\bash.exe bandle\\final_split_tool_win.sh \"%s\"",
             VENV_PATH);

    printf("Executing command:\n%s\n", cmd);

    return system(cmd);
}
