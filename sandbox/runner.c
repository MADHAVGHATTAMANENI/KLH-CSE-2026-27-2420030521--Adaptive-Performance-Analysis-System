#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>

/**
 * CompilerX POSIX High-Resolution Measurement Harness
 * 
 * Accurately measures:
 * - Wall-clock time (monotonic hardware clock)
 * - User-space CPU time (rusage)
 * - Kernel-space CPU time (rusage)
 * - Peak Resident Set Size (RSS) in KB
 * - Process exit code
 */

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <binary_path> [stdin_input]\n", argv[0]);
        return 1;
    }

    const char* binary_path = argv[1];
    const char* stdin_data = (argc > 2) ? argv[2] : "";

    int pipe_in[2];
    if (pipe(pipe_in) != 0) {
        perror("pipe failed");
        return 2;
    }

    struct timespec start_time, end_time;
    struct rusage usage_start, usage_end;

    // Use CLOCK_MONOTONIC_RAW if available, fallback to CLOCK_MONOTONIC
#ifdef CLOCK_MONOTONIC_RAW
    clock_gettime(CLOCK_MONOTONIC_RAW, &start_time);
#else
    clock_gettime(CLOCK_MONOTONIC, &start_time);
#endif

    getrusage(RUSAGE_CHILDREN, &usage_start);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return 3;
    }

    if (pid == 0) {
        // Child Process: Setup stdin redirection and execute binary
        close(pipe_in[1]);
        if (dup2(pipe_in[0], STDIN_FILENO) < 0) {
            perror("dup2 failed");
            exit(126);
        }
        close(pipe_in[0]);

        execl(binary_path, binary_path, (char*)NULL);
        perror("execl failed");
        exit(127);
    }

    // Parent Process: Pipe stdin payload to child and await termination
    close(pipe_in[0]);
    if (stdin_data != NULL && strlen(stdin_data) > 0) {
        ssize_t bytes_written = write(pipe_in[1], stdin_data, strlen(stdin_data));
        (void)bytes_written;
    }
    close(pipe_in[1]);

    int status;
    waitpid(pid, &status, 0);

#ifdef CLOCK_MONOTONIC_RAW
    clock_gettime(CLOCK_MONOTONIC_RAW, &end_time);
#else
    clock_gettime(CLOCK_MONOTONIC, &end_time);
#endif

    getrusage(RUSAGE_CHILDREN, &usage_end);

    double wall_time_ms = (double)(end_time.tv_sec - start_time.tv_sec) * 1000.0 +
                          (double)(end_time.tv_nsec - start_time.tv_nsec) / 1000000.0;

    double user_cpu_ms = (double)(usage_end.ru_utime.tv_sec - usage_start.ru_utime.tv_sec) * 1000.0 +
                         (double)(usage_end.ru_utime.tv_usec - usage_start.ru_utime.tv_usec) / 1000.0;

    double sys_cpu_ms = (double)(usage_end.ru_stime.tv_sec - usage_start.ru_stime.tv_sec) * 1000.0 +
                        (double)(usage_end.ru_stime.tv_usec - usage_start.ru_stime.tv_usec) / 1000.0;

    // Peak RSS: Linux reports in KB, macOS in bytes
    long peak_rss_kb = usage_end.ru_maxrss;
#ifdef __APPLE__
    peak_rss_kb = peak_rss_kb / 1024;
#endif

    int exit_code = -1;
    if (WIFEXITED(status)) {
        exit_code = WEXITSTATUS(status);
    } else if (WIFSIGNALED(status)) {
        exit_code = 128 + WTERMSIG(status);
    }

    // Emit single-line JSON format for backend parser
    printf("{\"wall_time_ms\": %.4f, \"user_cpu_ms\": %.4f, \"sys_cpu_ms\": %.4f, \"peak_memory_kb\": %ld, \"exit_code\": %d}\n",
           wall_time_ms, user_cpu_ms, sys_cpu_ms, peak_rss_kb, exit_code);

    return 0;
}
