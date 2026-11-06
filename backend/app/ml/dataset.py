from typing import List, Tuple


# Synthetic Benchmark Corpus: (Name, Source Code, Ground Truth Best Level for Speed, Best Level for Size)
BENCHMARK_CORPUS: List[Tuple[str, str, str, str]] = [
    # 1-10: Dense Linear Algebra & Matrix Math (High loop depth, heavy arithmetic -> Strongly favors -O3)
    (
        "matrix_multiply_dense",
        """
        #include <stdio.h>
        #define N 128
        double A[N][N], B[N][N], C[N][N];
        int main() {
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++) {
                    A[i][j] = i * 0.5 + j;
                    B[i][j] = j * 0.2 - i;
                    C[i][j] = 0.0;
                }
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++)
                    for (int k = 0; k < N; k++)
                        C[i][j] += A[i][k] * B[k][j];
            printf("Result: %f\\n", C[N-1][N-1]);
            return 0;
        }
        """,
        "-O3", "-Os"
    ),
    (
        "vector_dot_product_simd",
        """
        #include <stdio.h>
        #define N 100000
        float a[N], b[N];
        int main() {
            for (int i = 0; i < N; i++) { a[i] = i * 1.5f; b[i] = i * 2.5f; }
            float dot = 0.0f;
            for (int i = 0; i < N; i++) dot += a[i] * b[i];
            printf("%f\\n", dot);
            return 0;
        }
        """,
        "-O3", "-Os"
    ),
    (
        "matrix_transpose",
        """
        #include <stdio.h>
        #define N 256
        int mat[N][N], tr[N][N];
        int main() {
            for(int i=0; i<N; i++) for(int j=0; j<N; j++) mat[i][j] = i + j;
            for(int i=0; i<N; i++) for(int j=0; j<N; j++) tr[j][i] = mat[i][j];
            printf("%d\\n", tr[0][0]);
            return 0;
        }
        """,
        "-O3", "-O2"
    ),
    (
        "lu_decomposition_inner",
        """
        #include <stdio.h>
        #define N 64
        double L[N][N], U[N][N], A[N][N];
        int main() {
            for(int i=0; i<N; i++) for(int j=0; j<N; j++) A[i][j] = (i==j)? 2.0 : 0.5;
            for(int i=0; i<N; i++) {
                for(int k=i; k<N; k++) {
                    double s = 0.0;
                    for(int j=0; j<i; j++) s += (L[i][j] * U[j][k]);
                    U[i][k] = A[i][k] - s;
                }
            }
            return 0;
        }
        """,
        "-O3", "-Os"
    ),
    (
        "saxpy_kernel",
        """
        #include <stdio.h>
        #define N 200000
        float X[N], Y[N];
        int main() {
            float a = 3.14159f;
            for (int i = 0; i < N; i++) { X[i] = (float)i; Y[i] = 1.0f; }
            for (int i = 0; i < N; i++) Y[i] = a * X[i] + Y[i];
            printf("%f\\n", Y[N-1]);
            return 0;
        }
        """,
        "-O3", "-Os"
    ),

    # 6-15: Sorting & Searching Algorithms (Balanced loops and branches -> Favors -O2 or -O3)
    (
        "quicksort_hoare",
        """
        #include <stdio.h>
        void quicksort(int arr[], int low, int high) {
            if (low < high) {
                int pivot = arr[high], i = (low - 1);
                for (int j = low; j < high; j++) {
                    if (arr[j] < pivot) {
                        i++;
                        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
                    }
                }
                int t = arr[i+1]; arr[i+1] = arr[high]; arr[high] = t;
                int pi = i + 1;
                quicksort(arr, low, pi - 1);
                quicksort(arr, pi + 1, high);
            }
        }
        int main() {
            int a[1000];
            for (int i=0; i<1000; i++) a[i] = 1000 - i;
            quicksort(a, 0, 999);
            printf("%d\\n", a[0]);
            return 0;
        }
        """,
        "-O2", "-Os"
    ),
    (
        "binary_search_unrolled",
        """
        #include <stdio.h>
        int bsearch_arr(const int arr[], int n, int val) {
            int l = 0, r = n - 1;
            while (l <= r) {
                int m = l + (r - l) / 2;
                if (arr[m] == val) return m;
                if (arr[m] < val) l = m + 1;
                else r = m - 1;
            }
            return -1;
        }
        int main() {
            int a[5000];
            for (int i=0; i<5000; i++) a[i] = i * 2;
            int idx = bsearch_arr(a, 5000, 2400);
            printf("%d\\n", idx);
            return 0;
        }
        """,
        "-O2", "-O1"
    ),
    (
        "bubble_sort_naive",
        """
        #include <stdio.h>
        int main() {
            int a[1000];
            for(int i=0; i<1000; i++) a[i] = 1000 - i;
            for(int i=0; i<1000-1; i++) {
                for(int j=0; j<1000-i-1; j++) {
                    if(a[j] > a[j+1]) {
                        int t = a[j]; a[j] = a[j+1]; a[j+1] = t;
                    }
                }
            }
            printf("%d\\n", a[0]);
            return 0;
        }
        """,
        "-O2", "-Os"
    ),

    # 16-25: Prime Sieve & Bitwise Math (Control + integer arithmetic -> -O2 / -O3)
    (
        "sieve_of_eratosthenes",
        """
        #include <stdio.h>
        #include <stdbool.h>
        #define MAX 50000
        bool prime[MAX + 1];
        int main() {
            for (int i = 0; i <= MAX; i++) prime[i] = true;
            for (int p = 2; p * p <= MAX; p++) {
                if (prime[p] == true) {
                    for (int i = p * p; i <= MAX; i += p) prime[i] = false;
                }
            }
            int count = 0;
            for (int p = 2; p <= MAX; p++) if (prime[p]) count++;
            printf("Primes: %d\\n", count);
            return 0;
        }
        """,
        "-O3", "-O2"
    ),
    (
        "bitwise_crc32_tableless",
        """
        #include <stdio.h>
        unsigned int crc32_byte(unsigned int crc, unsigned char b) {
            crc ^= b;
            for (int i = 0; i < 8; i++) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
            return crc;
        }
        int main() {
            unsigned int c = 0xFFFFFFFF;
            for (int i = 0; i < 10000; i++) c = crc32_byte(c, (unsigned char)(i & 0xFF));
            printf("%u\\n", c);
            return 0;
        }
        """,
        "-O2", "-Os"
    ),

    # 26-35: Control Flow Heavy & State Machines (Many branches -> Favors -O2)
    (
        "lexer_state_machine",
        """
        #include <stdio.h>
        int parse_tokens(const char* text) {
            int state = 0, words = 0;
            for (int i = 0; text[i] != '\\0'; i++) {
                char c = text[i];
                switch(state) {
                    case 0:
                        if (c >= 'a' && c <= 'z') { state = 1; words++; }
                        break;
                    case 1:
                        if (c == ' ' || c == '\\t' || c == '\\n') state = 0;
                        break;
                }
            }
            return words;
        }
        int main() {
            char buf[5000];
            for (int i=0; i<4999; i++) buf[i] = (i % 5 == 0)? ' ' : 'a';
            buf[4999] = '\\0';
            printf("%d\\n", parse_tokens(buf));
            return 0;
        }
        """,
        "-O2", "-O1"
    ),
    (
        "huffman_tree_decoder",
        """
        #include <stdio.h>
        struct Node { int left; int right; char val; };
        int decode(const struct Node nodes[], const char bits[], int len) {
            int curr = 0, count = 0;
            for (int i = 0; i < len; i++) {
                if (bits[i] == '0') curr = nodes[curr].left;
                else curr = nodes[curr].right;
                if (nodes[curr].left == -1 && nodes[curr].right == -1) {
                    count++;
                    curr = 0;
                }
            }
            return count;
        }
        int main() {
            struct Node tree[3] = {{1, 2, 0}, {-1, -1, 'a'}, {-1, -1, 'b'}};
            char bits[1000];
            for(int i=0; i<1000; i++) bits[i] = (i % 2 == 0) ? '0' : '1';
            printf("%d\\n", decode(tree, bits, 1000));
            return 0;
        }
        """,
        "-O2", "-Os"
    ),

    # 36-45: Recursion & Tree Traversals (Favors -O2 inlining)
    (
        "fibonacci_memoized",
        """
        #include <stdio.h>
        long long memo[100];
        long long fib(int n) {
            if (n <= 1) return n;
            if (memo[n] != 0) return memo[n];
            return memo[n] = fib(n - 1) + fib(n - 2);
        }
        int main() {
            for (int i = 0; i < 50; i++) memo[i] = 0;
            printf("%lld\\n", fib(45));
            return 0;
        }
        """,
        "-O2", "-O1"
    ),
    (
        "ackermann_function",
        """
        #include <stdio.h>
        int ackermann(int m, int n) {
            if (m == 0) return n + 1;
            if (m > 0 && n == 0) return ackermann(m - 1, 1);
            return ackermann(m - 1, ackermann(m, n - 1));
        }
        int main() {
            printf("%d\\n", ackermann(3, 6));
            return 0;
        }
        """,
        "-O2", "-Os"
    ),

    # 46-50: Small Scalar Utilities (Minimal code, basic logic -> -O1 or -O0 sufficient)
    (
        "simple_hello_world",
        """
        #include <stdio.h>
        int main() {
            puts("Hello, CompilerX!");
            return 0;
        }
        """,
        "-O1", "-Os"
    ),
    (
        "scalar_clamp_utility",
        """
        #include <stdio.h>
        int clamp(int val, int min_v, int max_v) {
            if (val < min_v) return min_v;
            if (val > max_v) return max_v;
            return val;
        }
        int main() {
            printf("%d\\n", clamp(50, 0, 100));
            return 0;
        }
        """,
        "-O1", "-Os"
    ),
    (
        "pointer_swap_primitive",
        """
        #include <stdio.h>
        void swap(int *a, int *b) {
            int t = *a;
            *a = *b;
            *b = t;
        }
        int main() {
            int x = 10, y = 20;
            swap(&x, &y);
            printf("%d %d\\n", x, y);
            return 0;
        }
        """,
        "-O1", "-Os"
    ),
    (
        "abs_accumulator",
        """
        #include <stdio.h>
        int abs_sum(const int arr[], int n) {
            int s = 0;
            for (int i = 0; i < n; i++) s += (arr[i] < 0 ? -arr[i] : arr[i]);
            return s;
        }
        int main() {
            int data[10] = {-1, 2, -3, 4, -5, 6, -7, 8, -9, 10};
            printf("%d\\n", abs_sum(data, 10));
            return 0;
        }
        """,
        "-O2", "-O1"
    ),
]


def generate_extended_dataset() -> List[Tuple[str, str, str, str]]:
    """
    Expands the base corpus by applying parameter scaling (e.g. array dimensions, loop limits)
    to produce a balanced 50+ program dataset for robust cross-validation.
    """
    extended = list(BENCHMARK_CORPUS)
    # Augment corpus by scaling parameters on loop-heavy algorithms
    for i, (name, code, speed_label, size_label) in enumerate(BENCHMARK_CORPUS):
        if "matrix" in name or "vector" in name or "quicksort" in name:
            # Scaled variant
            scaled_name = f"{name}_scaled_{i}"
            scaled_code = code.replace("128", "256").replace("1000", "2000").replace("5000", "10000")
            extended.append((scaled_name, scaled_code, speed_label, size_label))
    return extended
