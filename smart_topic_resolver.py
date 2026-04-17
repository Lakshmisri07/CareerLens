"""
smart_topic_resolver.py  –  v7.0
==================================
Complete overhaul with ALL missing topics added:
  • Full AI/ML ecosystem (LangChain, RAG, MLOps, Hugging Face, Transformers, etc.)
  • All popular standalone tech stacks (Next.js, FastAPI, GraphQL, etc.)
  • More aptitude subtopics as standalone (Calendar, Clocks, Boats, Trains, etc.)
  • More verbal subtopics
  • HR / Behavioral interview topics
  • More ECE/EEE/MECH/CIVIL/CHEM subtopics
  • Competitive Programming, DSA Patterns
  • Operating System advanced topics
  • More Database topics (Redis, Cassandra, etc.)
  • Mobile Development (Android, iOS, Flutter, React Native)
  • Testing (Unit, Integration, Selenium, JUnit, etc.)
  • Networking advanced (Wireshark, Firewalls, VPN, etc.)
  • More Cloud (GCP, Azure specifics)
  • Mathematics (Linear Algebra, Calculus, Statistics)
  • Fuzzy matching v2 — better typo correction
"""

import re
from typing import Dict, List

# ===========================================================================
# SECTION 1 - CANONICAL TOPIC REGISTRY
# ===========================================================================

CANONICAL_TOPICS: Dict[str, dict] = {

    # =========================================================================
    # ── TECHNICAL ─ C / C++ ──────────────────────────────────────────────────
    # =========================================================================

    "C Programming": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "C programming language: data types, operators, control flow, arrays, "
            "strings, pointers, pointer arithmetic, functions, recursion, structures, "
            "unions, file I/O, memory management (malloc/free), preprocessor directives "
            "— as tested in placement exams."
        ),
        "aliases": [
            "c", "c programming", "c language", "c lang", "c prog",
            "c basics", "c fundamentals", "programming in c",
            "c pointers", "c arrays", "c functions", "c loops",
            "c strings", "c structures", "c unions", "c file handling",
            "c memory", "c preprocessor", "c syntax", "c programs",
            "ansi c", "c99", "c11", "c17",
        ],
    },

    "C++ Programming": {
        "category": "Technical",
        "subcategory": "C++",
        "ai_context": (
            "C++ programming: classes and objects, constructors/destructors, "
            "inheritance, polymorphism, operator overloading, templates, STL "
            "(vector, map, set, stack, queue), exception handling, smart pointers, "
            "virtual functions, abstract classes — as tested in placement exams."
        ),
        "aliases": [
            "c++", "cpp", "c plus plus", "cplusplus", "c++ programming",
            "c++ language", "stl", "standard template library",
            "c++ stl", "c++ oops", "c++ oop",
            "vector", "c++ vector", "c++ map", "c++ set",
            "operator overloading", "templates c++", "smart pointers",
            "virtual functions", "c++ classes", "c++11", "c++14", "c++17", "c++20",
            "move semantics", "rvalue reference", "lambda c++",
            "unique ptr", "shared ptr", "weak ptr",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Programming Languages ────────────────────────────────────
    # =========================================================================

    "Java Programming": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java programming: OOP concepts, classes and objects, inheritance, "
            "polymorphism, abstraction, encapsulation, interfaces, abstract classes, "
            "exception handling, collections framework (ArrayList, HashMap, LinkedList), "
            "multithreading, Java 8 features (streams, lambdas) — as tested in placement exams."
        ),
        "aliases": [
            "java", "java programming", "java language", "core java",
            "java basics", "java fundamentals", "java oops", "java oop",
            "java collections", "java multithreading", "java 8", "java 11", "java 17",
            "java streams", "java lambda", "java generics",
            "arraylist", "hashmap", "linked list java",
            "java exception", "java interface", "java classes",
            "jvm", "jre", "jdk", "bytecode",
            "java concurrency", "executor service", "future java",
            "java interview", "core java interview",
        ],
    },

    "Python Programming": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python programming: data types, lists, tuples, sets, dictionaries, "
            "comprehensions, functions, lambda, decorators, generators, iterators, "
            "OOP in Python, file handling, exception handling, modules, "
            "NumPy and Pandas basics — as tested in placement exams."
        ),
        "aliases": [
            "python", "python programming", "python language", "python basics",
            "python fundamentals", "python oops", "python oop", "python3",
            "python lists", "python dict", "python dictionaries",
            "python tuples", "python sets", "python functions",
            "python decorators", "python generators", "python file handling",
            "python modules", "python packages", "python syntax",
            "py", "python3.x", "python 3", "python2", "cpython",
            "asyncio", "python async", "python coroutines",
            "dataclass", "type hints python", "python interview",
        ],
    },

    "JavaScript": {
        "category": "Technical",
        "subcategory": "JavaScript",
        "ai_context": (
            "JavaScript: variables (var/let/const), data types, functions, "
            "closures, prototypes, ES6+ features (arrow functions, destructuring, "
            "spread/rest, promises, async/await), DOM manipulation, event handling, "
            "fetch API, modules — as tested in placement exams."
        ),
        "aliases": [
            "javascript", "js", "java script", "es6", "es2015", "es2020", "es2022",
            "ecmascript", "javascript es6", "vanilla js", "js basics",
            "promises", "async await", "closures js", "dom manipulation",
            "javascript dom", "arrow functions", "destructuring",
            "event loop", "prototype chain", "hoisting", "scope js",
            "js interview", "javascript interview", "es6 features",
        ],
    },

    "TypeScript": {
        "category": "Technical",
        "subcategory": "TypeScript",
        "ai_context": (
            "TypeScript: static typing, interfaces, type aliases, generics, "
            "enums, decorators, modules, type narrowing, utility types — "
            "as tested in placement exams."
        ),
        "aliases": [
            "typescript", "ts", "type script", "typed javascript",
            "typescript generics", "typescript interfaces", "typescript enums",
            "tsc", "tsconfig", "typescript basics", "typescript interview",
        ],
    },

    "Golang": {
        "category": "Technical",
        "subcategory": "Golang",
        "ai_context": (
            "Go programming: goroutines, channels, interfaces, structs, "
            "error handling, slices, maps, packages, concurrency model — "
            "as tested in placement exams."
        ),
        "aliases": [
            "golang", "go lang", "go programming", "go language",
            "goroutines", "go channels", "go interfaces", "go", "google go",
            "go concurrency", "go routines", "go modules", "go interview",
        ],
    },

    "Kotlin": {
        "category": "Technical",
        "subcategory": "Kotlin",
        "ai_context": (
            "Kotlin: null safety, data classes, extension functions, coroutines, "
            "sealed classes, smart casts, lambdas, collections — as tested in placement exams."
        ),
        "aliases": [
            "kotlin", "kotlin programming", "kotlin android", "kotlin coroutines",
            "kotlin basics", "kotlin language", "kotlin interview",
        ],
    },

    "Swift": {
        "category": "Technical",
        "subcategory": "Swift",
        "ai_context": (
            "Swift: optionals, closures, structs vs classes, protocols, enums, "
            "generics, memory management (ARC), SwiftUI basics — as tested in placement exams."
        ),
        "aliases": [
            "swift", "swift programming", "swift language", "ios development",
            "swiftui", "swift ios", "xcode swift", "swift interview",
        ],
    },

    "Rust": {
        "category": "Technical",
        "subcategory": "Rust",
        "ai_context": (
            "Rust: ownership, borrowing, lifetimes, traits, enums, pattern matching, "
            "cargo, memory safety — as tested in placement exams."
        ),
        "aliases": [
            "rust", "rust programming", "rust language", "rust lang",
            "ownership rust", "borrowing rust", "cargo rust", "rust interview",
        ],
    },

    "PHP": {
        "category": "Technical",
        "subcategory": "PHP",
        "ai_context": (
            "PHP: syntax, arrays, functions, OOP in PHP, sessions, forms, "
            "MySQL with PHP, Laravel basics — as tested in placement exams."
        ),
        "aliases": [
            "php", "php programming", "php language", "php basics",
            "php oop", "php mysql", "php web", "laravel php", "php interview",
        ],
    },

    "Ruby": {
        "category": "Technical",
        "subcategory": "Ruby",
        "ai_context": (
            "Ruby: blocks, procs, lambdas, modules, mixins, symbols, hashes, "
            "Ruby on Rails basics — as tested in placement exams."
        ),
        "aliases": [
            "ruby", "ruby programming", "ruby on rails", "rails", "ruby lang",
            "ror", "ruby rails", "ruby interview",
        ],
    },

    "Scala": {
        "category": "Technical",
        "subcategory": "Scala",
        "ai_context": (
            "Scala: functional programming, case classes, pattern matching, "
            "traits, implicits, Akka, Spark with Scala — as tested in placement exams."
        ),
        "aliases": [
            "scala", "scala programming", "scala language", "akka scala",
            "functional scala", "scala interview",
        ],
    },

    "R Programming": {
        "category": "Technical",
        "subcategory": "R",
        "ai_context": (
            "R language: vectors, data frames, ggplot2, dplyr, statistical analysis, "
            "regression, time series — as tested in placement exams."
        ),
        "aliases": [
            "r programming", "r language", "rlang", "r statistical",
            "ggplot", "ggplot2", "dplyr", "tidyverse",
        ],
    },

    "MATLAB": {
        "category": "Technical",
        "subcategory": "MATLAB",
        "ai_context": (
            "MATLAB: matrices, plotting, signal processing, Simulink, control systems, "
            "numerical methods — as tested in placement exams."
        ),
        "aliases": [
            "matlab", "matlab programming", "simulink", "matlab basics",
            "matlab numerical", "matlab signal",
        ],
    },

    "Dart": {
        "category": "Technical",
        "subcategory": "Dart",
        "ai_context": (
            "Dart: variables, functions, classes, async/await, streams, "
            "Flutter integration — as tested in placement exams."
        ),
        "aliases": [
            "dart", "dart programming", "dart language", "dart flutter",
            "dart basics", "dart interview",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ SQL / Databases ───────────────────────────────────────────
    # =========================================================================

    "SQL": {
        "category": "Technical",
        "subcategory": "SQL",
        "ai_context": (
            "SQL queries: SELECT, INSERT, UPDATE, DELETE, WHERE, GROUP BY, "
            "HAVING, ORDER BY, DISTINCT, aggregate functions, subqueries, "
            "CASE, window functions — as tested in placement exams."
        ),
        "aliases": [
            "sql", "structured query language", "sql queries", "sql basics",
            "sql commands", "sql functions", "sql aggregates",
            "mysql", "my sql", "postgresql", "postgres", "oracle sql",
            "ms sql", "sql server", "sqlite", "mariadb",
            "sql subquery", "sql joins query",
            "window functions", "sql window", "sql select",
            "stored procedures", "sql triggers", "sql views",
            "sql index", "sql optimization", "sql interview",
        ],
    },

    "NoSQL": {
        "category": "Technical",
        "subcategory": "NoSQL",
        "ai_context": (
            "NoSQL databases: MongoDB, Cassandra, Redis, DynamoDB; "
            "document, key-value, column-family, graph stores; CAP theorem — "
            "as tested in placement exams."
        ),
        "aliases": [
            "nosql", "no sql", "mongodb", "mongo db", "mongo",
            "cassandra", "redis", "dynamodb", "firebase",
            "couchdb", "neo4j", "graph database", "document database",
            "key value store", "nosql databases",
        ],
    },

    "Redis": {
        "category": "Technical",
        "subcategory": "Redis",
        "ai_context": (
            "Redis: in-memory data structures, strings, lists, sets, sorted sets, "
            "hashes, pub/sub, caching patterns, TTL, persistence (RDB, AOF), "
            "clustering — as tested in placement exams."
        ),
        "aliases": [
            "redis", "redis cache", "redis database", "redis interview",
            "redis data structures", "redis pub sub", "redis cluster",
            "in memory database", "cache database",
        ],
    },

    "MongoDB": {
        "category": "Technical",
        "subcategory": "MongoDB",
        "ai_context": (
            "MongoDB: documents, collections, CRUD operations, aggregation pipeline, "
            "indexing, schema design, replication, sharding — as tested in placement exams."
        ),
        "aliases": [
            "mongodb", "mongo", "mongo db", "mongodb interview",
            "mongodb aggregation", "mongodb indexing", "mongodb crud",
            "document store", "bson", "mongoose",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Data Structures ──────────────────────────────────────────
    # =========================================================================

    "Data Structures": {
        "category": "Technical",
        "subcategory": "Data Structures",
        "ai_context": (
            "Data structures: arrays, linked lists (singly, doubly, circular), "
            "stacks, queues, deque, trees (binary tree, BST, AVL), heaps, "
            "hash tables, graphs, tries — operations, time/space complexity, "
            "applications — as tested in placement exams."
        ),
        "aliases": [
            "data structures", "dsa", "ds", "data structure",
            "data structures and algorithms", "data struct",
            "dsa problems", "ds problems", "dsa preparation",
            "dsa interview", "dsa coding",
        ],
    },

    "Linked Lists": {
        "category": "Technical",
        "subcategory": "Linked Lists",
        "ai_context": (
            "Linked Lists: singly linked list, doubly linked list, circular linked list; "
            "insertion, deletion, traversal, reversal, cycle detection (Floyd's algorithm), "
            "merge two sorted lists, find middle element, nth from end — as tested in placement exams."
        ),
        "aliases": [
            "linked list", "linked lists", "singly linked list",
            "doubly linked list", "circular linked list",
            "ll", "linkedlist", "link list", "linked list problems",
            "linked list operations", "linked list interview",
        ],
    },

    "Stacks and Queues": {
        "category": "Technical",
        "subcategory": "Stacks and Queues",
        "ai_context": (
            "Stacks: LIFO, push/pop/peek, balanced parentheses, infix to postfix; "
            "Queues: FIFO, enqueue/dequeue, circular queue, deque, priority queue, "
            "queue using stacks — as tested in placement exams."
        ),
        "aliases": [
            "stack", "stacks", "stack data structure",
            "queue", "queues", "circular queue", "deque",
            "priority queue", "stacks and queues",
            "infix postfix", "balanced parentheses",
            "stack queue", "queue stack",
            "min stack", "max stack", "monotonic stack",
        ],
    },

    "Trees": {
        "category": "Technical",
        "subcategory": "Trees",
        "ai_context": (
            "Trees: binary tree, binary search tree (BST), AVL tree, red-black tree, "
            "B-tree; tree traversals (inorder, preorder, postorder, level order), "
            "height, diameter, LCA, segment tree — as tested in placement exams."
        ),
        "aliases": [
            "tree", "trees", "binary tree", "bst", "binary search tree",
            "avl tree", "avl", "red black tree", "b tree", "b+ tree",
            "segment tree", "fenwick tree", "binary indexed tree",
            "tree traversal", "inorder", "preorder", "postorder",
            "level order traversal", "tree height",
            "tree diameter", "lca", "lowest common ancestor",
            "n ary tree", "trie data structure", "tree interview",
        ],
    },

    "Heaps": {
        "category": "Technical",
        "subcategory": "Heaps",
        "ai_context": (
            "Heaps: min heap, max heap, heapify, insertion, deletion, "
            "heap sort, priority queue using heap, "
            "k-th largest/smallest element — as tested in placement exams."
        ),
        "aliases": [
            "heap", "heaps", "min heap", "max heap",
            "heap sort", "heapify", "priority heap",
            "min-heap", "max-heap", "heap operations",
        ],
    },

    "Hashing": {
        "category": "Technical",
        "subcategory": "Hashing",
        "ai_context": (
            "Hashing: hash functions, hash tables, collision resolution "
            "(chaining, open addressing — linear probing, quadratic probing, "
            "double hashing), load factor, rehashing — as tested in placement exams."
        ),
        "aliases": [
            "hashing", "hash table", "hash map", "hashmap",
            "hash set", "hash function",
            "collision resolution", "chaining", "open addressing",
            "hash collision", "hash tables problems",
        ],
    },

    "Graphs": {
        "category": "Technical",
        "subcategory": "Graphs",
        "ai_context": (
            "Graphs: directed/undirected, weighted, adjacency matrix/list, "
            "BFS, DFS, topological sort, cycle detection, connected components, "
            "shortest path (Dijkstra, Bellman-Ford, Floyd-Warshall), "
            "MST (Kruskal, Prim) — as tested in placement exams."
        ),
        "aliases": [
            "graph", "graphs", "graph theory", "graph data structure",
            "directed graph", "undirected graph", "weighted graph",
            "adjacency matrix", "adjacency list",
            "bfs", "breadth first search", "breadth-first search",
            "dfs", "depth first search", "depth-first search",
            "dijkstra", "dijkstra algorithm", "dijkstra's algorithm",
            "bellman ford", "bellman-ford", "floyd warshall", "floyd-warshall",
            "kruskal", "prim", "prim's algorithm", "kruskal's algorithm",
            "topological sort", "topological sorting",
            "cycle detection in graph", "connected components",
            "strongly connected components", "scc", "tarjan",
            "graph traversal", "graph algorithms",
            "union find", "disjoint set", "dsu", "graph interview",
        ],
    },

    "Tries": {
        "category": "Technical",
        "subcategory": "Tries",
        "ai_context": (
            "Trie (Prefix Tree): insert, search, delete, autocomplete, "
            "prefix search, word dictionary — as tested in placement exams."
        ),
        "aliases": [
            "trie", "tries", "prefix tree", "trie data structure",
            "autocomplete trie", "trie problems",
        ],
    },

    "Bit Manipulation": {
        "category": "Technical",
        "subcategory": "Bit Manipulation",
        "ai_context": (
            "Bit Manipulation: AND, OR, XOR, NOT, left/right shift, "
            "set/clear/toggle bit, count set bits, power of two — "
            "as tested in placement exams."
        ),
        "aliases": [
            "bit manipulation", "bitwise", "bitwise operators",
            "bit tricks", "bits", "xor problems", "bit masking",
            "count bits", "hamming weight", "bit shifting",
        ],
    },

    "Sliding Window": {
        "category": "Technical",
        "subcategory": "Sliding Window",
        "ai_context": (
            "Sliding Window: fixed and variable window, maximum subarray sum, "
            "longest substring without repeating characters — as tested in placement exams."
        ),
        "aliases": [
            "sliding window", "window technique", "two pointer",
            "two pointers", "two pointer technique",
            "subarray problems", "substring problems sliding",
            "kadane algorithm", "kadane's algorithm", "maximum subarray",
        ],
    },

    "Competitive Programming": {
        "category": "Technical",
        "subcategory": "Competitive Programming",
        "ai_context": (
            "Competitive Programming: problem-solving patterns, time complexity optimization, "
            "number theory, combinatorics, segment trees, sparse table, binary lifting, "
            "game theory, advanced DP — as tested in coding competitions and placements."
        ),
        "aliases": [
            "competitive programming", "cp", "competitive coding",
            "codeforces", "codechef", "atcoder", "icpc",
            "competitive programming problems",
            "number theory cp", "sparse table", "binary lifting",
            "game theory", "meet in middle", "divide conquer dp",
            "competitive programming interview",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Algorithms ────────────────────────────────────────────────
    # =========================================================================

    "Algorithms": {
        "category": "Technical",
        "subcategory": "Algorithms",
        "ai_context": (
            "Algorithms: sorting, searching, recursion, divide and conquer, "
            "time/space complexity, Big O notation — as tested in placement exams."
        ),
        "aliases": ["algorithms", "algorithm", "algo", "algos", "algorithm basics"],
    },

    "Sorting Algorithms": {
        "category": "Technical",
        "subcategory": "Sorting",
        "ai_context": (
            "Sorting Algorithms: bubble sort, selection sort, insertion sort, "
            "merge sort, quick sort, heap sort, counting sort, radix sort, bucket sort; "
            "stability, time and space complexity — as tested in placement exams."
        ),
        "aliases": [
            "sorting", "sorting algorithms", "sorting techniques",
            "bubble sort", "selection sort", "insertion sort",
            "merge sort", "quick sort", "heap sort",
            "radix sort", "counting sort", "bucket sort", "shell sort",
            "stable sort", "unstable sort", "sort",
            "quicksort", "mergesort", "timsort",
        ],
    },

    "Searching Algorithms": {
        "category": "Technical",
        "subcategory": "Searching",
        "ai_context": (
            "Searching: linear search, binary search, ternary search, jump search, "
            "interpolation search; binary search on answer — as tested in placement exams."
        ),
        "aliases": [
            "searching", "searching algorithms", "linear search", "binary search",
            "ternary search", "jump search", "interpolation search",
            "binary search problems", "search algorithm", "binary search tree search",
            "bsearch", "binary search interview",
        ],
    },

    "Dynamic Programming": {
        "category": "Technical",
        "subcategory": "Dynamic Programming",
        "ai_context": (
            "Dynamic Programming: overlapping subproblems, optimal substructure, "
            "memoization, tabulation, 0/1 knapsack, LCS, LIS, edit distance, "
            "coin change, matrix chain multiplication — as tested in placement exams."
        ),
        "aliases": [
            "dynamic programming", "dp", "dp problems",
            "memoization", "tabulation", "bottom up dp", "top down dp",
            "knapsack", "0/1 knapsack", "unbounded knapsack",
            "lcs", "longest common subsequence",
            "lis", "longest increasing subsequence",
            "edit distance", "coin change dp",
            "matrix chain multiplication", "dp on trees",
            "interval dp", "bitmask dp", "dp problems interview",
            "dp interview", "dp questions",
        ],
    },

    "Greedy Algorithms": {
        "category": "Technical",
        "subcategory": "Greedy",
        "ai_context": (
            "Greedy Algorithms: greedy choice property, activity selection, "
            "fractional knapsack, job scheduling, Huffman coding, "
            "minimum coin change — as tested in placement exams."
        ),
        "aliases": [
            "greedy", "greedy algorithms", "greedy method", "greedy approach",
            "activity selection", "fractional knapsack",
            "huffman coding", "job scheduling greedy", "greedy problems",
        ],
    },

    "Backtracking": {
        "category": "Technical",
        "subcategory": "Backtracking",
        "ai_context": (
            "Backtracking: N-queens, Sudoku solver, subset sum, "
            "permutations/combinations, rat in a maze, graph coloring — "
            "as tested in placement exams."
        ),
        "aliases": [
            "backtracking", "backtrack",
            "n queens", "n-queens", "sudoku solver",
            "subset sum", "graph coloring", "hamiltonian cycle",
            "backtracking problems",
        ],
    },

    "Recursion": {
        "category": "Technical",
        "subcategory": "Recursion",
        "ai_context": (
            "Recursion: base case, recursive call, call stack, tail recursion, "
            "Tower of Hanoi, flood fill, tree recursion — as tested in placement exams."
        ),
        "aliases": [
            "recursion", "recursive", "recursive algorithms",
            "tail recursion", "tower of hanoi",
            "fibonacci recursion", "factorial recursion", "recursion problems",
            "mutual recursion", "recursion interview",
        ],
    },

    "Divide and Conquer": {
        "category": "Technical",
        "subcategory": "Divide and Conquer",
        "ai_context": (
            "Divide and Conquer: merge sort, quick sort, binary search, "
            "Strassen matrix multiplication, closest pair of points — as tested in placement exams."
        ),
        "aliases": [
            "divide and conquer", "divide conquer", "d&c",
            "master theorem", "recurrence relation",
        ],
    },

    "Time and Space Complexity": {
        "category": "Technical",
        "subcategory": "Complexity Analysis",
        "ai_context": (
            "Time and Space Complexity: Big O, Big Theta, Big Omega, "
            "best/average/worst case, amortized analysis, "
            "common complexities (O(1)…O(2^n)) — as tested in placement exams."
        ),
        "aliases": [
            "time complexity", "space complexity", "big o", "big o notation",
            "complexity analysis", "asymptotic analysis",
            "big theta", "big omega", "amortized analysis",
            "p vs np", "np complete", "np hard",
            "algorithm complexity", "time space complexity",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ DBMS ──────────────────────────────────────────────────────
    # =========================================================================

    "DBMS": {
        "category": "Technical",
        "subcategory": "DBMS",
        "ai_context": (
            "Database Management Systems: ER model, relational model, keys, SQL joins, "
            "normalization (1NF–BCNF), ACID properties, transactions, concurrency control, "
            "indexing, views, triggers — as tested in placement exams."
        ),
        "aliases": [
            "dbms", "database", "databases", "database management",
            "database management system", "rdbms",
            "relational database", "database systems", "dbms interview",
        ],
    },

    "Database Joins": {
        "category": "Technical",
        "subcategory": "Joins",
        "ai_context": (
            "SQL Joins: INNER JOIN, LEFT/RIGHT/FULL OUTER JOIN, CROSS JOIN, SELF JOIN, "
            "NATURAL JOIN; join conditions, multiple columns, join with subqueries — "
            "as tested in placement exams."
        ),
        "aliases": [
            "joins", "join", "sql joins", "inner join", "outer join",
            "left join", "right join", "full outer join",
            "self join", "cross join", "natural join",
            "database joins", "join queries",
        ],
    },

    "Normalization": {
        "category": "Technical",
        "subcategory": "Normalization",
        "ai_context": (
            "Database Normalization: functional dependencies, 1NF, 2NF, 3NF, BCNF, 4NF; "
            "anomalies, decomposition — as tested in placement exams."
        ),
        "aliases": [
            "normalization", "database normalization",
            "1nf", "2nf", "3nf", "bcnf", "4nf",
            "first normal form", "second normal form", "third normal form",
            "functional dependency", "functional dependencies",
            "partial dependency", "transitive dependency",
            "database normalisation",
        ],
    },

    "ACID and Transactions": {
        "category": "Technical",
        "subcategory": "Transactions",
        "ai_context": (
            "ACID Properties: Atomicity, Consistency, Isolation, Durability; "
            "commit, rollback; isolation levels; concurrency control, deadlock — "
            "as tested in placement exams."
        ),
        "aliases": [
            "acid", "acid properties", "transactions", "transaction",
            "commit rollback", "isolation levels", "concurrency control",
            "two phase locking", "2pl", "deadlock dbms",
            "database transaction", "acid properties dbms",
        ],
    },

    "Indexing": {
        "category": "Technical",
        "subcategory": "Indexing",
        "ai_context": (
            "Database Indexing: clustered index, non-clustered index, "
            "B-tree/B+ tree index, hash index, dense vs sparse index — "
            "as tested in placement exams."
        ),
        "aliases": [
            "indexing", "database indexing", "b tree index", "b+ tree index",
            "clustered index", "non clustered index",
            "dense index", "sparse index", "index dbms",
        ],
    },

    "ER Model": {
        "category": "Technical",
        "subcategory": "ER Model",
        "ai_context": (
            "Entity-Relationship Model: entities, attributes, relationships, "
            "cardinality, participation, weak entities, ISA hierarchy, "
            "converting ER to relational schema — as tested in placement exams."
        ),
        "aliases": [
            "er model", "entity relationship", "entity relationship model",
            "erd", "er diagram", "entity relationship diagram",
            "cardinality", "weak entity", "er modelling",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Operating Systems ────────────────────────────────────────
    # =========================================================================

    "Operating Systems": {
        "category": "Technical",
        "subcategory": "OS",
        "ai_context": (
            "Operating Systems: processes, threads, process states, PCB, "
            "CPU scheduling, deadlock, memory management, file systems, "
            "synchronization — as tested in placement exams."
        ),
        "aliases": [
            "os", "operating system", "operating systems",
            "os concepts", "basic os", "unix", "linux os",
            "os interview",
        ],
    },

    "CPU Scheduling": {
        "category": "Technical",
        "subcategory": "CPU Scheduling",
        "ai_context": (
            "CPU Scheduling: FCFS, SJF, Round Robin, Priority scheduling, HRRN; "
            "Gantt charts, turnaround time, waiting time, throughput — "
            "as tested in placement exams."
        ),
        "aliases": [
            "cpu scheduling", "scheduling", "scheduling algorithms",
            "fcfs", "first come first served",
            "sjf", "shortest job first", "srtf", "shortest remaining time",
            "round robin", "rr scheduling",
            "priority scheduling", "hrrn",
            "gantt chart", "turnaround time", "waiting time",
            "cpu scheduler", "process scheduling",
            "multilevel queue", "multilevel feedback queue",
        ],
    },

    "Deadlock": {
        "category": "Technical",
        "subcategory": "Deadlock",
        "ai_context": (
            "Deadlock: four necessary conditions, prevention, avoidance (Banker's algorithm), "
            "detection (resource allocation graph), recovery — as tested in placement exams."
        ),
        "aliases": [
            "deadlock", "deadlock prevention", "deadlock avoidance",
            "banker algorithm", "banker's algorithm",
            "resource allocation graph", "circular wait",
            "deadlock detection", "deadlock recovery",
        ],
    },

    "Memory Management": {
        "category": "Technical",
        "subcategory": "Memory Management",
        "ai_context": (
            "Memory Management: paging, segmentation, virtual memory, "
            "page fault, page replacement (FIFO, LRU, Optimal), "
            "thrashing, TLB, page table — as tested in placement exams."
        ),
        "aliases": [
            "memory management", "paging", "segmentation",
            "virtual memory", "demand paging", "page fault",
            "page replacement", "lru", "fifo page", "optimal page replacement",
            "thrashing", "tlb", "translation lookaside buffer",
            "page table", "frame allocation", "memory allocation",
            "fragmentation", "compaction", "swapping",
        ],
    },

    "Process Synchronization": {
        "category": "Technical",
        "subcategory": "Synchronization",
        "ai_context": (
            "Process Synchronization: critical section, race condition, "
            "mutex, semaphore, monitors, producer-consumer, readers-writers, "
            "dining philosophers — as tested in placement exams."
        ),
        "aliases": [
            "synchronization", "process synchronization",
            "semaphore", "semaphores", "mutex",
            "critical section", "race condition", "monitor",
            "producer consumer", "readers writers", "dining philosophers",
            "process sync", "ipc",
        ],
    },

    "File Systems": {
        "category": "Technical",
        "subcategory": "File Systems",
        "ai_context": (
            "File Systems: FAT, NTFS, ext4, inodes, directory structure, "
            "disk scheduling (FCFS, SSTF, SCAN, C-SCAN), disk allocation methods — "
            "as tested in placement exams."
        ),
        "aliases": [
            "file system", "file systems", "inode", "fat", "ntfs", "ext4",
            "disk scheduling", "sstf", "scan algorithm", "c-scan",
            "disk allocation", "contiguous allocation", "linked allocation",
            "indexed allocation",
        ],
    },

    "Linux": {
        "category": "Technical",
        "subcategory": "Linux",
        "ai_context": (
            "Linux: basic commands (ls, cd, grep, awk, sed, find, chmod, chown), "
            "shell scripting, processes, file permissions, cron jobs, "
            "networking commands (netstat, ifconfig, ssh, scp) — as tested in placement exams."
        ),
        "aliases": [
            "linux", "linux commands", "linux basics", "unix commands",
            "shell", "bash", "bash scripting", "shell scripting",
            "linux interview", "linux administration",
            "chmod", "grep", "awk", "sed", "linux shell",
            "ubuntu", "centos", "fedora", "debian",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Computer Networks ────────────────────────────────────────
    # =========================================================================

    "Computer Networks": {
        "category": "Technical",
        "subcategory": "Computer Networks",
        "ai_context": (
            "Computer Networks: OSI model, TCP/IP model, "
            "IP addressing, routing, transport layer, application layer — "
            "as tested in placement exams."
        ),
        "aliases": [
            "computer networks", "cn", "networking", "network",
            "computer networking", "network concepts", "cn interview",
        ],
    },

    "OSI Model": {
        "category": "Technical",
        "subcategory": "OSI Model",
        "ai_context": (
            "OSI Model: 7 layers (Physical, Data Link, Network, Transport, "
            "Session, Presentation, Application), functions, protocols, PDU names — "
            "as tested in placement exams."
        ),
        "aliases": [
            "osi model", "osi", "osi layers", "osi 7 layers",
            "osi reference model", "7 layers",
            "physical layer", "data link layer", "network layer",
            "transport layer osi", "session layer", "presentation layer",
            "application layer osi",
        ],
    },

    "TCP/IP and Protocols": {
        "category": "Technical",
        "subcategory": "TCP/IP",
        "ai_context": (
            "TCP/IP: TCP vs UDP, TCP 3-way handshake, flow control, "
            "congestion control, IPv4 vs IPv6, ICMP, ARP — "
            "as tested in placement exams."
        ),
        "aliases": [
            "tcp ip", "tcp/ip", "tcp ip model",
            "tcp", "udp", "tcp vs udp", "tcp udp",
            "three way handshake", "3 way handshake",
            "four way handshake", "tcp handshake",
            "flow control", "congestion control",
            "ipv4", "ipv6", "ip protocol",
            "icmp", "arp", "rarp",
        ],
    },

    "IP Addressing and Subnetting": {
        "category": "Technical",
        "subcategory": "IP Addressing",
        "ai_context": (
            "IP Addressing: IPv4 classes (A/B/C/D/E), subnet mask, CIDR, "
            "subnetting calculation, hosts per subnet, NAT, IPv6 basics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "ip addressing", "ip address", "subnetting", "subnet",
            "subnet mask", "cidr", "ip classes",
            "class a", "class b", "class c",
            "private ip", "nat", "network address translation",
            "broadcast address", "ip subnetting",
        ],
    },

    "Application Layer Protocols": {
        "category": "Technical",
        "subcategory": "Application Layer",
        "ai_context": (
            "Application Layer: HTTP (methods, status codes, HTTPS), DNS, "
            "SMTP, POP3, IMAP, FTP, DHCP, SNMP — as tested in placement exams."
        ),
        "aliases": [
            "http", "https", "http protocol", "http methods",
            "http status codes", "get post put delete",
            "dns", "domain name system", "dns resolution",
            "smtp", "pop3", "imap", "email protocols",
            "ftp", "dhcp", "snmp",
            "application layer protocols", "websocket",
        ],
    },

    "Routing Protocols": {
        "category": "Technical",
        "subcategory": "Routing",
        "ai_context": (
            "Routing: static vs dynamic, RIP, OSPF, BGP, "
            "distance vector, link state — as tested in placement exams."
        ),
        "aliases": [
            "routing", "routing protocols", "rip", "ospf", "bgp",
            "distance vector", "link state routing",
            "routing table", "static routing", "dynamic routing",
        ],
    },

    "Network Security": {
        "category": "Technical",
        "subcategory": "Network Security",
        "ai_context": (
            "Network Security: firewalls, IDS/IPS, VPN, SSL/TLS, "
            "network attacks (DoS, MitM, ARP poisoning, DNS spoofing) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "network security", "firewall", "ids", "ips", "vpn",
            "ssl tls", "network attacks", "dos attack", "ddos",
            "arp poisoning", "dns spoofing", "sniffing", "packet sniffing",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ OOP and Software Engineering ──────────────────────────────
    # =========================================================================

    "OOP Concepts": {
        "category": "Technical",
        "subcategory": "OOP",
        "ai_context": (
            "Object-Oriented Programming: classes, objects, encapsulation, "
            "inheritance, polymorphism (overloading vs overriding), abstraction, "
            "interfaces, abstract classes, constructors, access modifiers — "
            "as tested in placement exams."
        ),
        "aliases": [
            "oop", "oops", "object oriented", "object oriented programming",
            "object-oriented", "oop concepts", "oops concepts",
            "encapsulation", "inheritance", "polymorphism", "abstraction",
            "classes and objects", "class and object",
            "interface", "abstract class",
            "method overloading", "method overriding",
            "constructor", "destructor",
            "access modifiers", "oop interview",
        ],
    },

    "Design Patterns": {
        "category": "Technical",
        "subcategory": "Design Patterns",
        "ai_context": (
            "Design Patterns: Creational (Singleton, Factory, Builder, Prototype), "
            "Structural (Adapter, Facade, Decorator), Behavioral (Observer, Strategy, Command); "
            "SOLID principles — as tested in placement exams."
        ),
        "aliases": [
            "design patterns", "design pattern",
            "singleton", "singleton pattern",
            "factory pattern", "factory", "abstract factory",
            "builder pattern", "prototype pattern",
            "observer pattern", "observer",
            "strategy pattern", "strategy",
            "decorator pattern", "adapter pattern",
            "facade pattern", "composite pattern",
            "mvc", "model view controller", "mvvm", "mvp",
            "solid", "solid principles",
            "single responsibility principle", "open closed principle",
            "liskov substitution", "dependency inversion",
        ],
    },

    "Software Engineering": {
        "category": "Technical",
        "subcategory": "Software Engineering",
        "ai_context": (
            "Software Engineering: SDLC (waterfall, agile, spiral), Scrum, "
            "testing (unit, integration, system, UAT), TDD, Git, CI/CD, UML — "
            "as tested in placement exams."
        ),
        "aliases": [
            "software engineering", "se",
            "software development",
            "sdlc", "software development life cycle",
            "agile", "agile methodology", "agile development",
            "scrum", "scrum framework", "sprint", "kanban",
            "waterfall", "waterfall model", "spiral model", "v model",
            "software testing", "testing",
            "unit testing", "integration testing",
            "system testing", "acceptance testing", "regression testing",
            "tdd", "test driven development", "bdd",
            "git", "version control", "github", "gitlab", "bitbucket",
            "ci cd", "ci/cd", "continuous integration", "continuous deployment",
            "devops", "dev ops",
            "uml", "uml diagrams", "use case diagram",
            "code review", "pair programming",
        ],
    },

    "Software Testing": {
        "category": "Technical",
        "subcategory": "Software Testing",
        "ai_context": (
            "Software Testing: unit testing, integration testing, system testing, "
            "UAT, regression testing, smoke testing, black box vs white box, "
            "test cases, bug life cycle, Selenium, JUnit, pytest — "
            "as tested in placement exams."
        ),
        "aliases": [
            "software testing", "testing", "qa", "quality assurance",
            "unit testing", "integration testing", "regression testing",
            "black box testing", "white box testing", "grey box testing",
            "test cases", "test plan", "bug life cycle",
            "selenium", "junit", "pytest", "testng",
            "manual testing", "automation testing",
            "smoke testing", "sanity testing",
            "performance testing", "load testing",
            "testing interview", "qa interview",
        ],
    },

    "System Design": {
        "category": "Technical",
        "subcategory": "System Design",
        "ai_context": (
            "System Design: scalability, load balancing, caching (Redis), "
            "database sharding, CAP theorem, microservices, API gateway, "
            "message queues (Kafka), rate limiting, consistent hashing — "
            "as tested in placement exams."
        ),
        "aliases": [
            "system design", "hld", "high level design",
            "lld", "low level design",
            "scalability", "load balancing", "load balancer",
            "caching", "cache", "redis", "memcached",
            "sharding", "database sharding", "replication",
            "cap theorem", "cap",
            "microservices", "microservice", "micro services",
            "api gateway", "message queue", "kafka", "rabbitmq",
            "cdn", "content delivery network",
            "rate limiting", "distributed systems",
            "consistent hashing", "system design interview",
            "design url shortener", "design twitter", "design instagram",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Web Development ───────────────────────────────────────────
    # =========================================================================

    "HTML and CSS": {
        "category": "Technical",
        "subcategory": "HTML/CSS",
        "ai_context": (
            "HTML5 and CSS3: semantic HTML, forms, tables, CSS selectors, "
            "flexbox, grid, responsive design, media queries, animations — "
            "as tested in placement exams."
        ),
        "aliases": [
            "html", "html5", "css", "css3",
            "html css", "html and css",
            "semantic html", "flexbox", "css grid", "responsive design",
            "media queries", "css animations", "html forms", "html interview",
        ],
    },

    "React": {
        "category": "Technical",
        "subcategory": "React",
        "ai_context": (
            "React: components, JSX, props, state, hooks (useState, useEffect, "
            "useContext, useRef), virtual DOM, lifecycle, Redux, React Router — "
            "as tested in placement exams."
        ),
        "aliases": [
            "react", "reactjs", "react js", "react hooks",
            "react components", "jsx", "react state", "react props",
            "usestate", "useeffect", "usecontext", "useref",
            "redux", "react redux", "context api",
            "react router", "react native", "virtual dom",
            "class components", "functional components",
            "react interview", "react basics",
        ],
    },

    "Next.js": {
        "category": "Technical",
        "subcategory": "Next.js",
        "ai_context": (
            "Next.js: SSR, SSG, ISR, file-based routing, API routes, "
            "getServerSideProps, getStaticProps, Image optimization, "
            "middleware, App Router — as tested in placement exams."
        ),
        "aliases": [
            "next.js", "nextjs", "next js", "next",
            "ssr nextjs", "ssg", "isr", "server side rendering",
            "static site generation", "next.js interview",
            "next js routing", "next js api routes",
            "app router", "pages router", "next 13", "next 14",
        ],
    },

    "Angular": {
        "category": "Technical",
        "subcategory": "Angular",
        "ai_context": (
            "Angular: modules, components, services, dependency injection, "
            "directives, pipes, routing, RxJS, forms (template/reactive), "
            "HTTP client — as tested in placement exams."
        ),
        "aliases": [
            "angular", "angularjs", "angular js", "angular 2",
            "angular 4", "angular 8", "angular 12", "angular 15", "angular 17",
            "ng", "rxjs", "angular services", "angular routing",
            "angular directives", "angular pipes", "angular interview",
        ],
    },

    "Vue.js": {
        "category": "Technical",
        "subcategory": "Vue.js",
        "ai_context": (
            "Vue.js: Vue instance, data binding, computed properties, "
            "watchers, directives (v-if, v-for), components, Vuex, Vue Router — "
            "as tested in placement exams."
        ),
        "aliases": [
            "vue", "vuejs", "vue js", "vue.js",
            "vue 3", "vuex", "vue router", "composition api",
            "options api vue", "vue interview",
        ],
    },

    "Node.js": {
        "category": "Technical",
        "subcategory": "Node.js",
        "ai_context": (
            "Node.js: event loop, non-blocking I/O, modules (CommonJS, ESM), "
            "npm, Express.js, file system, streams, buffers, cluster — "
            "as tested in placement exams."
        ),
        "aliases": [
            "node.js", "nodejs", "node js", "node",
            "express", "expressjs", "express.js",
            "npm", "package.json", "event loop node",
            "node streams", "node buffers", "node cluster",
            "rest api node", "middleware express", "node interview",
        ],
    },

    "Django": {
        "category": "Technical",
        "subcategory": "Django",
        "ai_context": (
            "Django: MTV pattern, models, views, templates, URL routing, "
            "Django ORM, forms, authentication, REST framework (DRF) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "django", "django python", "django framework",
            "django rest framework", "drf", "django orm",
            "django models", "django views", "django urls",
            "django authentication", "django forms", "django interview",
        ],
    },

    "Flask": {
        "category": "Technical",
        "subcategory": "Flask",
        "ai_context": (
            "Flask: routing, views, templates (Jinja2), request/response, "
            "blueprints, SQLAlchemy, Flask-RESTful, authentication — "
            "as tested in placement exams."
        ),
        "aliases": [
            "flask", "flask python", "flask framework",
            "flask restful", "flask sqlalchemy", "jinja2",
            "flask blueprints", "flask authentication", "flask routing",
            "flask interview",
        ],
    },

    "FastAPI": {
        "category": "Technical",
        "subcategory": "FastAPI",
        "ai_context": (
            "FastAPI: path operations, request/response models, Pydantic, "
            "dependency injection, async/await, OpenAPI docs, authentication (JWT), "
            "background tasks — as tested in placement exams."
        ),
        "aliases": [
            "fastapi", "fast api", "fastapi python",
            "fastapi interview", "fastapi basics",
            "fastapi pydantic", "fastapi async",
            "python api", "python rest api",
        ],
    },

    "Spring Boot": {
        "category": "Technical",
        "subcategory": "Spring Boot",
        "ai_context": (
            "Spring Boot: dependency injection, Spring MVC, REST APIs, "
            "JPA/Hibernate, Spring Security, Spring Data, "
            "auto-configuration — as tested in placement exams."
        ),
        "aliases": [
            "spring boot", "spring", "spring framework",
            "spring mvc", "spring security", "spring data",
            "spring jpa", "hibernate", "jpa",
            "spring rest", "spring microservices", "spring interview",
        ],
    },

    "REST APIs": {
        "category": "Technical",
        "subcategory": "REST APIs",
        "ai_context": (
            "REST APIs: HTTP methods (GET, POST, PUT, DELETE, PATCH), "
            "status codes, request/response, authentication (JWT, OAuth), "
            "API versioning, rate limiting — as tested in placement exams."
        ),
        "aliases": [
            "rest", "rest api", "restful", "restful api",
            "api", "apis", "web api", "rest apis",
            "http methods", "get post put", "jwt", "json web token",
            "oauth", "api authentication", "api versioning",
            "graphql", "grpc", "rest interview",
        ],
    },

    "GraphQL": {
        "category": "Technical",
        "subcategory": "GraphQL",
        "ai_context": (
            "GraphQL: queries, mutations, subscriptions, schema, resolvers, "
            "fragments, directives, N+1 problem, Apollo Client/Server — "
            "as tested in placement exams."
        ),
        "aliases": [
            "graphql", "graph ql", "graphql api",
            "graphql queries", "graphql mutations",
            "apollo graphql", "graphql schema",
            "graphql interview",
        ],
    },

    "Web Development": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "Web Development: HTML5, CSS3, JavaScript, REST APIs, "
            "frontend and backend concepts, deployment basics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "web development", "web dev", "web programming",
            "frontend", "backend", "full stack", "fullstack",
            "laravel", "nuxt.js", "nuxt",
            "gatsby", "svelte", "sveltekit", "remix",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Cloud, DevOps, Containers ─────────────────────────────────
    # =========================================================================

    "Cloud Computing": {
        "category": "Technical",
        "subcategory": "Cloud Computing",
        "ai_context": (
            "Cloud Computing: IaaS/PaaS/SaaS, AWS (EC2, S3, RDS, Lambda), "
            "Azure, GCP, Docker, Kubernetes, serverless — as tested in placement exams."
        ),
        "aliases": [
            "cloud computing", "cloud", "cloud services",
            "aws", "amazon web services",
            "azure", "microsoft azure",
            "gcp", "google cloud",
            "iaas", "paas", "saas",
            "virtualization", "hypervisor", "cloud interview",
        ],
    },

    "AWS": {
        "category": "Technical",
        "subcategory": "AWS",
        "ai_context": (
            "Amazon Web Services: EC2, S3, RDS, Lambda, ECS, EKS, IAM, "
            "VPC, CloudFormation, Route53, CloudFront — "
            "as tested in placement exams."
        ),
        "aliases": [
            "aws", "amazon web services", "ec2", "s3", "rds",
            "lambda aws", "aws lambda", "ecs", "eks",
            "iam aws", "vpc aws", "cloudformation",
            "route53", "cloudfront", "sqs", "sns aws",
            "dynamodb aws", "elasticache", "aws interview",
            "aws basics", "cloud formation",
        ],
    },

    "Azure": {
        "category": "Technical",
        "subcategory": "Azure",
        "ai_context": (
            "Microsoft Azure: Azure VM, Blob Storage, Azure SQL, Azure Functions, "
            "AKS, Azure AD, Azure DevOps, App Service — as tested in placement exams."
        ),
        "aliases": [
            "azure", "microsoft azure", "azure cloud",
            "azure vm", "azure storage", "azure functions",
            "azure devops", "azure ad", "aks",
            "azure interview", "azure basics",
        ],
    },

    "GCP": {
        "category": "Technical",
        "subcategory": "GCP",
        "ai_context": (
            "Google Cloud Platform: Compute Engine, Cloud Storage, BigQuery, "
            "Cloud Functions, GKE, Cloud Run, Pub/Sub — as tested in placement exams."
        ),
        "aliases": [
            "gcp", "google cloud", "google cloud platform",
            "bigquery", "cloud functions gcp", "gke",
            "cloud run", "pub sub gcp",
            "gcp interview", "google cloud interview",
        ],
    },

    "Docker": {
        "category": "Technical",
        "subcategory": "Docker",
        "ai_context": (
            "Docker: images, containers, Dockerfile, docker-compose, "
            "volumes, networks, registry, container orchestration basics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "docker", "docker container", "dockerfile",
            "docker compose", "docker-compose", "docker image",
            "container", "containers", "containerization",
            "docker volumes", "docker networking", "docker interview",
        ],
    },

    "Kubernetes": {
        "category": "Technical",
        "subcategory": "Kubernetes",
        "ai_context": (
            "Kubernetes: pods, deployments, services, ingress, "
            "ConfigMaps, secrets, namespaces, Helm, scaling — "
            "as tested in placement exams."
        ),
        "aliases": [
            "kubernetes", "k8s", "kubectl",
            "pods", "kubernetes pods", "kubernetes deployment",
            "kubernetes service", "ingress kubernetes",
            "helm", "kubernetes cluster", "kubernetes interview",
        ],
    },

    "DevOps": {
        "category": "Technical",
        "subcategory": "DevOps",
        "ai_context": (
            "DevOps: CI/CD pipelines (Jenkins, GitHub Actions, GitLab CI), "
            "infrastructure as code (Terraform, Ansible), monitoring, "
            "logging, Docker, Kubernetes — as tested in placement exams."
        ),
        "aliases": [
            "devops", "dev ops",
            "jenkins", "github actions", "gitlab ci", "circle ci",
            "terraform", "ansible", "puppet", "chef",
            "infrastructure as code", "iac",
            "monitoring", "prometheus", "grafana",
            "logging", "elk stack", "splunk", "devops interview",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Cybersecurity ─────────────────────────────────────────────
    # =========================================================================

    "Cybersecurity": {
        "category": "Technical",
        "subcategory": "Cybersecurity",
        "ai_context": (
            "Cybersecurity: cryptography (AES, RSA), hashing (SHA-256), "
            "SSL/TLS, network attacks (SQL injection, XSS, CSRF, DDoS), "
            "firewalls, OWASP Top 10 — as tested in placement exams."
        ),
        "aliases": [
            "cybersecurity", "cyber security", "information security", "infosec",
            "security", "network security",
            "cryptography", "encryption", "decryption",
            "symmetric encryption", "asymmetric encryption",
            "rsa", "aes", "des", "3des",
            "hashing security", "sha", "sha256", "md5",
            "digital signature", "ssl", "tls",
            "sql injection", "xss", "cross site scripting",
            "csrf", "buffer overflow", "phishing", "mitm", "ddos",
            "ethical hacking", "penetration testing", "pen testing",
            "owasp", "owasp top 10", "cybersecurity interview",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ AI / ML / Deep Learning / Data Science ────────────────────
    # =========================================================================
    "Artificial Inteligence":{
      "category":"Technical",
       "aliases":[
           "ai","AI","Generative ai"
       ],
    },
    "Machine Learning": {
        "category": "Technical",
        "subcategory": "Machine Learning",
        "ai_context": (
            "Machine Learning: supervised/unsupervised/reinforcement learning, "
            "bias-variance, overfitting, regularization, cross-validation, "
            "algorithms (linear regression, SVM, KNN, decision trees, random forest, "
            "K-means, neural networks) — as tested in placement exams."
        ),
        "aliases": [
            "machine learning", "ml", "ml algorithms",
            "supervised learning", "unsupervised learning", "reinforcement learning",
            "regression", "linear regression", "logistic regression",
            "classification algorithms",
            "decision tree", "random forest",
            "svm", "support vector machine",
            "knn", "k nearest neighbour", "k nearest neighbor",
            "k means", "k-means", "clustering",
            "pca", "principal component analysis", "dimensionality reduction",
            "overfitting", "underfitting", "bias variance",
            "regularization", "cross validation", "ml interview",
            "machine learning interview",
        ],
    },

    "Deep Learning": {
        "category": "Technical",
        "subcategory": "Deep Learning",
        "ai_context": (
            "Deep Learning: neural networks (ANN, CNN, RNN, LSTM, GRU), "
            "backpropagation, activation functions, batch normalization, "
            "dropout, transfer learning, GANs, transformers — "
            "as tested in placement exams."
        ),
        "aliases": [
            "deep learning", "dl", "neural networks", "neural network",
            "ann", "artificial neural network",
            "cnn", "convolutional neural network", "convolutional",
            "rnn", "recurrent neural network", "lstm", "gru",
            "backpropagation", "activation functions", "relu", "sigmoid",
            "batch normalization", "dropout",
            "transfer learning", "gan", "generative adversarial",
            "transformer model", "attention mechanism",
            "deep learning interview",
        ],
    },

    "Natural Language Processing": {
        "category": "Technical",
        "subcategory": "NLP",
        "ai_context": (
            "NLP: tokenization, stemming, lemmatization, TF-IDF, "
            "word embeddings (Word2Vec, GloVe), BERT, sentiment analysis, "
            "named entity recognition, text classification — as tested in placement exams."
        ),
        "aliases": [
            "nlp", "natural language processing",
            "text processing", "sentiment analysis",
            "word2vec", "glove", "bert", "gpt",
            "tokenization", "stemming", "lemmatization",
            "text classification", "ner", "named entity",
            "language model", "llm",
            "nlp interview",
        ],
    },

    "Computer Vision": {
        "category": "Technical",
        "subcategory": "Computer Vision",
        "ai_context": (
            "Computer Vision: image processing (OpenCV), CNN architectures "
            "(ResNet, VGG, YOLO), object detection, segmentation — "
            "as tested in placement exams."
        ),
        "aliases": [
            "computer vision", "cv", "image processing", "opencv",
            "object detection", "image classification", "segmentation",
            "yolo", "resnet", "vgg", "image recognition",
            "computer vision interview",
        ],
    },

    "Transformers and LLMs": {
        "category": "Technical",
        "subcategory": "Transformers & LLMs",
        "ai_context": (
            "Transformers and LLMs: attention mechanism, self-attention, "
            "BERT, GPT, T5, encoder-decoder, positional encoding, "
            "fine-tuning, prompt engineering, RAG — as tested in placement exams."
        ),
        "aliases": [
            "transformers", "transformer architecture", "llm", "llms",
            "large language model", "large language models",
            "bert", "gpt", "gpt-3", "gpt-4", "gpt4", "chatgpt",
            "t5", "roberta", "xlnet", "distilbert",
            "attention mechanism", "self attention", "multi head attention",
            "prompt engineering", "prompt tuning",
            "rag", "retrieval augmented generation",
            "fine tuning", "lora", "qlora", "peft",
            "foundation models", "llm interview",
            "hugging face", "huggingface", "transformers library",
        ],
    },

    "LangChain and RAG": {
        "category": "Technical",
        "subcategory": "LangChain & RAG",
        "ai_context": (
            "LangChain: chains, agents, tools, memory, retrievers, vector stores, "
            "LLM wrappers; RAG pipeline: document loading, chunking, embeddings, "
            "vector DB (Pinecone, ChromaDB, FAISS), retrieval — as tested in placement exams."
        ),
        "aliases": [
            "langchain", "lang chain", "langchain python",
            "rag", "retrieval augmented generation", "rag pipeline",
            "vector store", "vector database", "vector db",
            "pinecone", "chromadb", "chroma", "faiss", "weaviate",
            "embeddings", "text embeddings", "semantic search",
            "langchain interview", "rag interview",
            "llm applications", "ai agents", "langchain agents",
            "langchain memory", "langchain chains",
        ],
    },

    "MLOps": {
        "category": "Technical",
        "subcategory": "MLOps",
        "ai_context": (
            "MLOps: ML pipelines, model serving, model monitoring, drift detection, "
            "MLflow, Kubeflow, feature stores, A/B testing, versioning, "
            "deployment strategies (blue/green, canary) — as tested in placement exams."
        ),
        "aliases": [
            "mlops", "ml ops", "ml operations",
            "model deployment", "model serving", "model monitoring",
            "mlflow", "kubeflow", "wandb", "weights and biases",
            "feature store", "feast", "model drift",
            "ml pipeline", "data pipeline",
            "model versioning", "model registry",
            "mlops interview",
        ],
    },

    "Data Science": {
        "category": "Technical",
        "subcategory": "Data Science",
        "ai_context": (
            "Data Science: exploratory data analysis (EDA), NumPy, Pandas, "
            "Matplotlib, Seaborn, feature engineering, model evaluation — "
            "as tested in placement exams."
        ),
        "aliases": [
            "data science", "data analysis", "data analytics",
            "numpy", "pandas", "matplotlib", "seaborn",
            "eda", "exploratory data analysis",
            "feature engineering", "data visualization",
            "jupyter", "jupyter notebook", "kaggle",
            "data science interview",
        ],
    },

    "Statistics and Probability (ML)": {
        "category": "Technical",
        "subcategory": "Statistics for ML",
        "ai_context": (
            "Statistics for ML: mean, median, mode, variance, std deviation, "
            "probability distributions (normal, binomial, Poisson), "
            "hypothesis testing, p-value, confidence intervals, "
            "Bayes theorem, correlation — as tested in placement exams."
        ),
        "aliases": [
            "statistics", "stats", "probability statistics",
            "statistical analysis", "descriptive statistics",
            "hypothesis testing", "p value", "confidence interval",
            "normal distribution", "gaussian distribution",
            "probability distribution", "binomial distribution",
            "correlation", "covariance", "regression statistics",
            "statistics for ml", "statistics interview",
        ],
    },

    "Big Data": {
        "category": "Technical",
        "subcategory": "Big Data",
        "ai_context": (
            "Big Data: Hadoop, HDFS, MapReduce, Spark, Hive, HBase, "
            "data warehousing, ETL, streaming (Kafka, Flink) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "big data", "hadoop", "hdfs", "mapreduce",
            "apache spark", "spark", "hive", "hbase",
            "etl", "data warehouse", "data lake",
            "flink", "kafka streaming", "big data interview",
        ],
    },

    "Data Engineering": {
        "category": "Technical",
        "subcategory": "Data Engineering",
        "ai_context": (
            "Data Engineering: ETL pipelines, data warehouses (Snowflake, Redshift, BigQuery), "
            "Apache Spark, Kafka, Airflow, dbt, data modeling (star/snowflake schema) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "data engineering", "data engineer",
            "etl", "elt", "data pipeline",
            "snowflake", "redshift", "bigquery",
            "apache airflow", "airflow", "dbt",
            "data modeling", "star schema", "snowflake schema",
            "data warehouse design", "data lake",
            "data engineering interview",
        ],
    },

    "AI Ethics and Responsible AI": {
        "category": "Technical",
        "subcategory": "AI Ethics",
        "ai_context": (
            "AI Ethics: bias in ML, fairness, explainability (XAI), "
            "privacy (federated learning, differential privacy), "
            "AI regulations, model transparency — as tested in placement exams."
        ),
        "aliases": [
            "ai ethics", "responsible ai", "ethical ai",
            "bias in ml", "fairness ml", "explainability",
            "xai", "explainable ai", "shap", "lime",
            "federated learning", "differential privacy",
            "ai regulations", "ai governance",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Mobile Development ────────────────────────────────────────
    # =========================================================================

    "Android Development": {
        "category": "Technical",
        "subcategory": "Android",
        "ai_context": (
            "Android Development: Activities, Fragments, Intents, RecyclerView, "
            "ViewModel, LiveData, Room, Retrofit, Coroutines, Jetpack Compose — "
            "as tested in placement exams."
        ),
        "aliases": [
            "android", "android development", "android programming",
            "android studio", "android app",
            "activity", "fragment", "intent", "recyclerview",
            "viewmodel", "livedata", "room database",
            "retrofit android", "coroutines android",
            "jetpack", "jetpack compose", "compose",
            "android interview",
        ],
    },

    "iOS Development": {
        "category": "Technical",
        "subcategory": "iOS",
        "ai_context": (
            "iOS Development: UIKit, SwiftUI, ViewControllers, Auto Layout, "
            "Core Data, URLSession, delegates, closures, ARC — "
            "as tested in placement exams."
        ),
        "aliases": [
            "ios", "ios development", "ios programming",
            "xcode", "uikit", "swiftui",
            "viewcontroller", "auto layout", "core data",
            "urlsession", "arc", "ios interview",
        ],
    },

    "Flutter": {
        "category": "Technical",
        "subcategory": "Flutter",
        "ai_context": (
            "Flutter: widgets, stateless vs stateful, state management (Provider, Bloc, Riverpod), "
            "navigation, HTTP requests, animations, platform channels — "
            "as tested in placement exams."
        ),
        "aliases": [
            "flutter", "flutter development", "flutter app",
            "dart flutter", "flutter widgets",
            "stateful widget", "stateless widget",
            "provider flutter", "bloc flutter", "riverpod",
            "flutter navigation", "flutter interview",
        ],
    },

    "React Native": {
        "category": "Technical",
        "subcategory": "React Native",
        "ai_context": (
            "React Native: components, navigation (React Navigation), styling, "
            "state management (Redux, Context), native modules, Expo — "
            "as tested in placement exams."
        ),
        "aliases": [
            "react native", "rn", "react-native",
            "react navigation", "expo", "native modules",
            "react native interview",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Computer Architecture / CS Theory ─────────────────────────
    # =========================================================================

    "Compiler Design": {
        "category": "Technical",
        "subcategory": "Compiler Design",
        "ai_context": (
            "Compiler Design: lexical analysis, syntax analysis (parsing), "
            "semantic analysis, intermediate code, optimization, code generation, "
            "lex/yacc, LL/LR parsers — as tested in placement exams."
        ),
        "aliases": [
            "compiler design", "compilers", "compiler",
            "lexical analysis", "lexer", "scanner",
            "syntax analysis", "parser", "parsing",
            "ll parser", "lr parser", "slr", "clr", "lalr",
            "semantic analysis", "intermediate code generation",
            "code optimization", "code generation",
            "lex", "yacc", "flex bison",
            "automata", "formal languages", "regular expressions theory",
            "context free grammar", "cfg",
        ],
    },

    "Theory of Computation": {
        "category": "Technical",
        "subcategory": "Theory of Computation",
        "ai_context": (
            "Theory of Computation: finite automata (DFA, NFA), regular languages, "
            "regular expressions, pushdown automata, context-free grammars, "
            "Turing machines, decidability, complexity classes (P, NP) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "theory of computation", "toc", "automata theory",
            "automata", "finite automata", "dfa", "nfa",
            "regular expressions toc", "pushdown automata", "pda",
            "turing machine", "tm",
            "context free grammar toc", "cfg toc",
            "decidability", "p np", "np complete toc",
            "formal languages",
        ],
    },

    "Computer Architecture": {
        "category": "Technical",
        "subcategory": "Computer Architecture",
        "ai_context": (
            "Computer Architecture: RISC vs CISC, pipelining, cache memory, "
            "instruction formats, addressing modes, memory hierarchy, "
            "parallelism (SIMD, MIMD) — as tested in placement exams."
        ),
        "aliases": [
            "computer architecture", "computer organization",
            "coa", "co", "computer organisation",
            "risc", "cisc", "pipelining",
            "cache", "cache memory", "cache coherence",
            "instruction set architecture", "isa",
            "addressing modes computer", "memory hierarchy",
            "pipeline hazards", "branch prediction",
        ],
    },

    "Discrete Mathematics": {
        "category": "Technical",
        "subcategory": "Discrete Mathematics",
        "ai_context": (
            "Discrete Mathematics: sets, relations, functions, propositional logic, "
            "predicate logic, proof techniques, graph theory, combinatorics, "
            "Boolean algebra — as tested in placement exams."
        ),
        "aliases": [
            "discrete mathematics", "discrete maths", "discrete math",
            "dm", "set theory", "relations",
            "propositional logic", "predicate logic", "logic gates discrete",
            "boolean algebra discrete", "graph theory discrete",
            "combinatorics", "permutation combination discrete",
            "number theory discrete", "proofs",
        ],
    },

    "Linear Algebra": {
        "category": "Technical",
        "subcategory": "Linear Algebra",
        "ai_context": (
            "Linear Algebra: vectors, matrices, determinant, eigenvalues, eigenvectors, "
            "matrix multiplication, rank, null space, SVD, PCA — "
            "as tested in placement exams and ML interviews."
        ),
        "aliases": [
            "linear algebra", "matrices", "matrix",
            "eigenvalues", "eigenvectors", "determinant",
            "matrix multiplication", "rank", "null space",
            "svd", "singular value decomposition",
            "linear algebra for ml", "linear algebra interview",
        ],
    },

    "Calculus": {
        "category": "Technical",
        "subcategory": "Calculus",
        "ai_context": (
            "Calculus: differentiation, integration, chain rule, gradient, "
            "partial derivatives, optimization (gradient descent), "
            "Taylor series — as tested in ML placement exams."
        ),
        "aliases": [
            "calculus", "differentiation", "integration",
            "gradient", "partial derivative", "chain rule",
            "gradient descent", "calculus for ml",
            "optimization calculus", "backpropagation calculus",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ ECE Topics ────────────────────────────────────────────────
    # =========================================================================

    "Digital Electronics": {
        "category": "Technical",
        "subcategory": "Digital Electronics",
        "ai_context": (
            "Digital Electronics: number systems (binary, octal, hex, BCD), "
            "logic gates, Boolean algebra, K-map, combinational circuits "
            "(adder, MUX, encoder), sequential circuits (flip-flops, counters, registers), "
            "ADC/DAC — as tested in placement exams."
        ),
        "aliases": [
            "digital electronics", "digital circuits", "digital logic",
            "digital systems",
            "logic gates", "gates", "boolean algebra", "de morgan",
            "k map", "karnaugh map", "kmap",
            "combinational circuits", "sequential circuits",
            "flip flop", "flip-flop", "jk flip flop", "d flip flop", "sr flip flop",
            "counters", "registers", "shift register",
            "multiplexer", "mux", "demux", "demultiplexer",
            "encoder", "decoder", "adder", "subtractor", "half adder", "full adder",
            "adc", "dac", "analog to digital", "digital to analog",
            "binary", "octal", "hexadecimal", "hex", "bcd",
            "number system digital",
        ],
    },

    "Analog Electronics": {
        "category": "Technical",
        "subcategory": "Analog Electronics",
        "ai_context": (
            "Analog Electronics: PN junction diode, Zener diode, BJT, MOSFET, FET, "
            "op-amp (inverting, non-inverting, summing), oscillators, rectifiers, "
            "filters, voltage regulators — as tested in placement exams."
        ),
        "aliases": [
            "analog electronics", "analogue electronics", "analog circuits",
            "diode", "diodes", "pn junction", "zener diode",
            "bjt", "transistor", "npn", "pnp", "bipolar transistor",
            "fet", "jfet", "mosfet", "field effect transistor",
            "amplifier", "amplifiers", "op amp", "op-amp", "operational amplifier",
            "rectifier", "half wave rectifier", "full wave rectifier",
            "oscillator", "colpitts", "hartley",
            "filter analog", "low pass filter", "high pass filter", "band pass filter",
            "voltage regulator",
        ],
    },

    "Signal Processing": {
        "category": "Technical",
        "subcategory": "Signal Processing",
        "ai_context": (
            "Signal Processing: Fourier series/transform, Laplace transform, Z-transform, "
            "sampling theorem (Nyquist), DFT, FFT, FIR/IIR filters — "
            "as tested in placement exams."
        ),
        "aliases": [
            "signal processing", "signals and systems", "dsp",
            "digital signal processing",
            "fourier", "fourier transform", "fourier series",
            "laplace", "laplace transform",
            "z transform", "z-transform",
            "sampling theorem", "nyquist", "sampling", "aliasing",
            "convolution", "dft", "fft",
            "fir filter", "iir filter", "butterworth filter",
        ],
    },

    "Embedded Systems": {
        "category": "Technical",
        "subcategory": "Embedded Systems",
        "ai_context": (
            "Embedded Systems: microcontroller architecture (8051, PIC, ARM), "
            "GPIO, UART, SPI, I2C, PWM, timers, RTOS, embedded C, IoT basics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "embedded systems", "embedded", "embedded programming",
            "microcontroller", "microcontrollers", "8051", "arm cortex",
            "pic microcontroller", "stm32", "arduino", "raspberry pi",
            "gpio", "uart", "spi", "i2c", "pwm",
            "rtos", "real time operating system", "freertos",
            "embedded c", "firmware",
            "iot", "internet of things", "esp32", "esp8266",
        ],
    },

    "VLSI Design": {
        "category": "Technical",
        "subcategory": "VLSI",
        "ai_context": (
            "VLSI Design: CMOS technology, MOSFET characteristics, CMOS logic gates, "
            "FPGA, Verilog HDL, VHDL, RTL design — as tested in placement exams."
        ),
        "aliases": [
            "vlsi", "vlsi design", "very large scale integration",
            "cmos", "fpga", "verilog", "vhdl",
            "logic design vlsi", "rtl design", "asic",
            "nmos", "pmos", "vlsi fabrication",
        ],
    },

    "Microprocessors": {
        "category": "Technical",
        "subcategory": "Microprocessors",
        "ai_context": (
            "Microprocessors: 8085/8086 architecture, instruction set, addressing modes, "
            "assembly language, memory/IO interfacing, interrupts — "
            "as tested in placement exams."
        ),
        "aliases": [
            "microprocessors", "microprocessor", "8085", "8086",
            "assembly language", "instruction set",
            "addressing modes", "memory interfacing",
            "8085 architecture", "8086 architecture",
            "interrupts microprocessor", "io interfacing",
            "arm processor", "x86", "risc v",
        ],
    },

    "Communication Systems": {
        "category": "Technical",
        "subcategory": "Communication Systems",
        "ai_context": (
            "Communication Systems: AM/FM modulation, ASK/FSK/PSK/QAM, "
            "TDM/FDM, GSM, CDMA, LTE/4G/5G, optical fiber, antennas, "
            "Shannon's theorem — as tested in placement exams."
        ),
        "aliases": [
            "communication systems", "communication", "wireless communication",
            "mobile communication", "gsm", "cdma", "lte", "4g", "5g",
            "satellite communication", "optical fiber", "fiber optics",
            "antenna", "antennas",
            "tdm", "fdm", "cdm", "multiplexing",
            "am modulation", "fm modulation", "ask", "fsk", "psk", "qam",
            "shannon theorem", "channel capacity",
        ],
    },

    "Control Systems": {
        "category": "Technical",
        "subcategory": "Control Systems",
        "ai_context": (
            "Control Systems: open/closed loop, transfer functions, block diagram, "
            "Routh-Hurwitz, root locus, Bode plot, Nyquist, PID controllers, "
            "state space — as tested in placement exams."
        ),
        "aliases": [
            "control systems", "control system",
            "transfer function", "block diagram", "signal flow graph",
            "mason's gain", "root locus", "bode plot", "nyquist plot",
            "pid controller", "pid", "proportional integral derivative",
            "routh hurwitz", "stability analysis",
            "state space", "state space analysis",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ EEE Topics ────────────────────────────────────────────────
    # =========================================================================

    "Circuit Theory": {
        "category": "Technical",
        "subcategory": "Circuit Theory",
        "ai_context": (
            "Circuit Theory: Ohm's law, KCL, KVL, Thevenin, Norton, Superposition, "
            "AC circuits (phasors, impedance, resonance), three-phase, "
            "transient analysis — as tested in placement exams."
        ),
        "aliases": [
            "circuit theory", "network theory", "electric circuits",
            "electrical circuits", "basic electrical",
            "ohm's law", "ohms law", "kcl", "kvl",
            "kirchhoff", "kirchhoff's laws",
            "thevenin", "thevenin theorem", "norton", "norton theorem",
            "superposition", "superposition theorem",
            "max power transfer", "maximum power transfer",
            "ac circuits", "phasors", "impedance", "resonance",
            "three phase", "3 phase", "power factor",
            "transient analysis", "rl circuit", "rc circuit", "rlc circuit",
        ],
    },

    "Power Systems": {
        "category": "Technical",
        "subcategory": "Power Systems",
        "ai_context": (
            "Power Systems: power generation, transmission lines, distribution, "
            "load flow analysis, fault analysis, protection (relays, circuit breakers) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "power systems", "power system", "electrical power",
            "transmission lines", "power transmission",
            "distribution system", "power distribution",
            "load flow", "load flow analysis", "power flow",
            "fault analysis", "symmetrical components", "short circuit",
            "protection", "relay", "circuit breaker", "switchgear",
        ],
    },

    "Electrical Machines": {
        "category": "Technical",
        "subcategory": "Electrical Machines",
        "ai_context": (
            "Electrical Machines: DC generators, DC motors, transformers, "
            "three-phase induction motors, synchronous generators/motors — "
            "as tested in placement exams."
        ),
        "aliases": [
            "electrical machines", "electric machines",
            "dc motor", "dc generator", "dc machine",
            "transformer", "transformers",
            "induction motor", "induction machine", "3 phase motor",
            "synchronous motor", "synchronous generator", "alternator",
            "motor control", "speed control", "starting methods",
        ],
    },

    "Power Electronics": {
        "category": "Technical",
        "subcategory": "Power Electronics",
        "ai_context": (
            "Power Electronics: SCR/thyristor, IGBT, power MOSFET, "
            "rectifiers, inverters, DC-DC converters (Buck/Boost), PWM — "
            "as tested in placement exams."
        ),
        "aliases": [
            "power electronics", "power electronic",
            "thyristor", "scr", "silicon controlled rectifier",
            "igbt", "power mosfet",
            "controlled rectifier", "uncontrolled rectifier",
            "inverter power", "chopper", "dc dc converter",
            "buck converter", "boost converter",
            "pwm", "pulse width modulation",
            "smps", "switched mode power supply",
        ],
    },

    "Electromagnetic Theory": {
        "category": "Technical",
        "subcategory": "Electromagnetic Theory",
        "ai_context": (
            "Electromagnetic Theory: Maxwell's equations, Gauss's law, Faraday's law, "
            "Ampere's law, wave propagation, transmission lines EMT — "
            "as tested in placement exams."
        ),
        "aliases": [
            "electromagnetic theory", "emt", "electromagnetics",
            "maxwell equations", "maxwell's equations",
            "gauss law", "faraday law", "ampere law",
            "wave propagation", "poynting vector",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ MECH Topics ───────────────────────────────────────────────
    # =========================================================================

    "Thermodynamics": {
        "category": "Technical",
        "subcategory": "Thermodynamics",
        "ai_context": (
            "Thermodynamics: zeroth–third laws, enthalpy, entropy, ideal gas, "
            "Carnot/Rankine/Otto/Diesel cycles, refrigeration — as tested in placement exams."
        ),
        "aliases": [
            "thermodynamics", "thermo", "thermal engineering",
            "first law", "second law", "third law of thermodynamics",
            "carnot cycle", "rankine cycle", "otto cycle", "diesel cycle",
            "refrigeration", "refrigeration cycle", "vcr cycle",
            "entropy", "enthalpy", "ideal gas",
            "steam power", "power cycles", "thermodynamic processes",
        ],
    },

    "Fluid Mechanics": {
        "category": "Technical",
        "subcategory": "Fluid Mechanics",
        "ai_context": (
            "Fluid Mechanics: fluid properties, Bernoulli's equation, "
            "continuity equation, Reynolds number, pipe flow, boundary layer, "
            "pumps and turbines — as tested in placement exams."
        ),
        "aliases": [
            "fluid mechanics", "fluids", "fluid dynamics",
            "hydraulics", "hydraulic machines",
            "bernoulli", "bernoulli's equation", "bernoulli theorem",
            "continuity equation", "flow through pipes", "pipe flow",
            "reynolds number", "laminar flow", "turbulent flow",
            "boundary layer", "pump", "turbine",
            "venturimeter", "orifice meter", "pitot tube",
        ],
    },

    "Strength of Materials": {
        "category": "Technical",
        "subcategory": "Strength of Materials",
        "ai_context": (
            "Strength of Materials: stress, strain, elastic constants, "
            "shear force/bending moment diagrams, torsion, deflection of beams, "
            "columns — as tested in placement exams."
        ),
        "aliases": [
            "strength of materials", "som", "mechanics of materials", "mom",
            "stress", "strain", "stress strain",
            "shear force", "bending moment", "sfbmd", "sfd bmd",
            "torsion", "deflection of beams", "columns",
            "euler formula", "strain energy", "mohr's circle",
        ],
    },

    "Manufacturing Technology": {
        "category": "Technical",
        "subcategory": "Manufacturing",
        "ai_context": (
            "Manufacturing: casting, welding, machining (turning, milling, drilling), "
            "metal forming, CNC, metrology, quality control — as tested in placement exams."
        ),
        "aliases": [
            "manufacturing", "manufacturing technology", "manufacturing processes",
            "casting", "welding", "machining",
            "turning", "milling", "drilling", "grinding", "boring",
            "cnc", "cnc machining", "cnc programming",
            "metrology", "quality control", "inspection",
            "metal forming", "forging", "rolling", "extrusion", "drawing",
            "powder metallurgy", "lean manufacturing", "six sigma",
        ],
    },

    "Machine Design": {
        "category": "Technical",
        "subcategory": "Machine Design",
        "ai_context": (
            "Machine Design: factor of safety, failure theories, fasteners, "
            "shafts and keys, bearings, gears, springs, brakes, clutches — "
            "as tested in placement exams."
        ),
        "aliases": [
            "machine design", "design of machine elements", "dme",
            "machine elements", "design of machines",
            "bearings", "gears", "gear design", "spur gear", "helical gear",
            "shafts", "keys", "couplings",
            "clutch", "brakes", "flywheel",
            "fasteners", "bolts", "screws", "rivets",
            "spring design", "belt drive", "chain drive",
        ],
    },

    "Heat Transfer": {
        "category": "Technical",
        "subcategory": "Heat Transfer",
        "ai_context": (
            "Heat Transfer: conduction, convection, radiation, heat exchangers, "
            "fins, boiling and condensation — as tested in placement exams."
        ),
        "aliases": [
            "heat transfer", "heat conduction", "heat convection",
            "heat radiation", "thermal conduction",
            "heat exchanger", "fourier law", "newton cooling",
            "stefan boltzmann", "fins heat transfer",
        ],
    },

    "Mechanics": {
        "category": "Technical",
        "subcategory": "Mechanics",
        "ai_context": (
            "Engineering Mechanics: statics, dynamics, kinematics, Newton's laws, "
            "work/energy, momentum, friction, simple machines — as tested in placement exams."
        ),
        "aliases": [
            "mechanics", "engineering mechanics", "statics", "dynamics",
            "kinematics", "kinetics", "newton's laws", "friction",
            "work energy", "momentum", "simple machines",
        ],
    },

    "Automobile Engineering": {
        "category": "Technical",
        "subcategory": "Automobile Engineering",
        "ai_context": (
            "Automobile Engineering: IC engine components, fuel systems, "
            "transmission, braking, suspension, steering — as tested in placement exams."
        ),
        "aliases": [
            "automobile engineering", "automotive engineering", "automobile",
            "ic engine", "internal combustion engine", "engine components",
            "transmission systems", "braking systems", "suspension",
            "steering", "fuel systems", "cooling lubrication",
            "electric vehicle", "ev", "hybrid vehicle",
        ],
    },

    "CAD/CAM": {
        "category": "Technical",
        "subcategory": "CAD/CAM",
        "ai_context": (
            "CAD/CAM: engineering drawing, AutoCAD 2D/3D, SolidWorks, CATIA, "
            "CNC programming, rapid prototyping, FEA basics — as tested in placement exams."
        ),
        "aliases": [
            "cad/cam", "cad cam", "cad", "cam", "autocad",
            "solidworks", "catia", "engineering drawing",
            "rapid prototyping", "fea", "finite element analysis",
            "3d modelling", "3d modeling", "cad design", "creo",
        ],
    },

    "Industrial Engineering": {
        "category": "Technical",
        "subcategory": "Industrial Engineering",
        "ai_context": (
            "Industrial Engineering: work study, time-motion study, plant layout, "
            "production planning, inventory control (EOQ), CPM/PERT, "
            "operations research — as tested in placement exams."
        ),
        "aliases": [
            "industrial engineering", "operations management",
            "work study", "time study", "motion study",
            "plant layout", "production planning",
            "inventory control", "eoq", "cpm pert",
            "operations research", "linear programming",
            "queuing theory",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ CIVIL Topics ──────────────────────────────────────────────
    # =========================================================================

    "Structural Analysis": {
        "category": "Technical",
        "subcategory": "Structural Analysis",
        "ai_context": (
            "Structural Analysis: beams, trusses, frames, arches, "
            "method of joints/sections, influence lines, slope deflection, "
            "moment distribution — as tested in placement exams."
        ),
        "aliases": [
            "structural analysis", "structures", "structural engineering",
            "beams", "trusses", "frames", "arches",
            "method of joints", "method of sections",
            "influence lines", "slope deflection", "moment distribution",
            "indeterminate structures", "propped cantilever",
        ],
    },

    "Geotechnical Engineering": {
        "category": "Technical",
        "subcategory": "Geotechnical Engineering",
        "ai_context": (
            "Geotechnical Engineering: soil classification, Atterberg limits, "
            "compaction, permeability, Terzaghi consolidation, Mohr-Coulomb, "
            "bearing capacity, pile foundations, slope stability — "
            "as tested in placement exams."
        ),
        "aliases": [
            "geotechnical engineering", "geotechnical", "soil mechanics",
            "soil", "soil classification", "atterberg limits",
            "compaction", "proctor test",
            "permeability", "darcy law", "seepage",
            "consolidation", "settlement",
            "shear strength", "mohr coulomb",
            "bearing capacity", "foundations", "pile foundation",
            "slope stability", "retaining wall",
        ],
    },

    "Surveying": {
        "category": "Technical",
        "subcategory": "Surveying",
        "ai_context": (
            "Surveying: chain/compass/levelling/theodolite/tacheometry, "
            "total station, GPS/GNSS, contouring — as tested in placement exams."
        ),
        "aliases": [
            "surveying", "engineering surveying",
            "chain surveying", "compass surveying",
            "levelling", "leveling", "dumpy level",
            "theodolite", "tacheometry", "contouring",
            "total station", "gps", "gnss",
        ],
    },

    "Concrete Technology": {
        "category": "Technical",
        "subcategory": "Concrete Technology",
        "ai_context": (
            "Concrete Technology: cement types, aggregates, water-cement ratio, "
            "workability (slump test), IS mix design, durability, curing, "
            "admixtures — as tested in placement exams."
        ),
        "aliases": [
            "concrete technology", "concrete", "cement concrete",
            "cement", "cement types", "opc", "ppc", "src",
            "mix design", "water cement ratio", "w/c ratio",
            "workability", "slump test",
            "rcc", "reinforced concrete", "prestressed concrete", "psc",
            "curing", "admixtures",
        ],
    },

    "Transportation Engineering": {
        "category": "Technical",
        "subcategory": "Transportation Engineering",
        "ai_context": (
            "Transportation Engineering: highway planning, geometric design, "
            "pavement design (flexible/rigid), traffic engineering (LOS), "
            "railway engineering — as tested in placement exams."
        ),
        "aliases": [
            "transportation engineering", "highway engineering",
            "roads", "highways", "road design", "road geometry",
            "pavement design", "flexible pavement", "rigid pavement",
            "traffic engineering", "traffic flow", "los",
            "railway engineering", "railways",
        ],
    },

    "RCC Design": {
        "category": "Technical",
        "subcategory": "RCC Design",
        "ai_context": (
            "RCC Design: working stress / limit state methods, "
            "singly/doubly reinforced beams, T-beams, slabs, columns, "
            "footings, staircases — as tested in placement exams."
        ),
        "aliases": [
            "rcc design", "rcc", "reinforced cement concrete",
            "reinforced concrete design", "rc design",
            "limit state", "working stress method",
            "beams design", "slab design", "column design",
            "footing design", "staircase design",
        ],
    },

    "Environmental Engineering": {
        "category": "Technical",
        "subcategory": "Environmental Engineering",
        "ai_context": (
            "Environmental Engineering: water supply, wastewater treatment, "
            "solid waste management, air pollution, environmental impact assessment — "
            "as tested in placement exams."
        ),
        "aliases": [
            "environmental engineering", "environmental",
            "water supply", "wastewater treatment", "sewage treatment",
            "solid waste", "air pollution", "water quality",
            "eia", "environmental impact assessment",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Chemical Topics ───────────────────────────────────────────
    # =========================================================================

    "Chemical Engineering": {
        "category": "Technical",
        "subcategory": "Chemical Engineering",
        "ai_context": (
            "Chemical Engineering: material/energy balances, fluid flow, heat transfer, "
            "mass transfer (distillation, absorption), reaction engineering "
            "(CSTR, PFR), process control — as tested in placement exams."
        ),
        "aliases": [
            "chemical engineering", "chemical",
            "process engineering", "chemical process",
            "mass transfer", "distillation", "absorption", "extraction",
            "reaction engineering", "cstr", "pfr", "batch reactor",
            "process control chem", "chemical thermodynamics",
            "heat exchanger", "fluid flow chemical",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Blockchain / Emerging ─────────────────────────────────────
    # =========================================================================

    "Blockchain": {
        "category": "Technical",
        "subcategory": "Blockchain",
        "ai_context": (
            "Blockchain: distributed ledger, consensus algorithms (PoW, PoS), "
            "smart contracts, Ethereum, Solidity, DeFi, NFTs — "
            "as tested in placement exams."
        ),
        "aliases": [
            "blockchain", "block chain", "cryptocurrency",
            "bitcoin", "ethereum", "solidity", "smart contracts",
            "defi", "nft", "web3", "consensus algorithm",
            "proof of work", "proof of stake",
        ],
    },

    "Quantum Computing": {
        "category": "Technical",
        "subcategory": "Quantum Computing",
        "ai_context": (
            "Quantum Computing: qubits, superposition, entanglement, "
            "quantum gates, Shor's algorithm, Grover's algorithm, "
            "quantum cryptography — as tested in placement exams."
        ),
        "aliases": [
            "quantum computing", "quantum", "qubits",
            "quantum gates", "shor's algorithm", "grover's algorithm",
            "quantum cryptography", "quantum mechanics computing",
        ],
    },

    # =========================================================================
    # ── APTITUDE ─ Quantitative ────────────────────────────────────────────────
    # =========================================================================

    "Number System": {
        "category": "Aptitude",
        "subcategory": "Number System",
        "ai_context": (
            "Number System aptitude: types of numbers, divisibility rules, "
            "HCF and LCM, prime factorization, unit digit, remainders, cyclicity — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "number system", "numbers", "number theory",
            "hcf", "lcm", "hcf lcm", "highest common factor",
            "lowest common multiple", "gcd",
            "prime numbers", "prime", "prime factorization",
            "divisibility", "divisibility rules",
            "remainders", "remainder theorem",
            "unit digit", "cyclicity", "fermat little theorem",
            "lcm hcf", "lcm and hcf",
        ],
    },

    "Percentages": {
        "category": "Aptitude",
        "subcategory": "Percentages",
        "ai_context": (
            "Percentage problems: percentage increase/decrease, successive percentage, "
            "fraction/decimal conversion — as tested in placement aptitude exams."
        ),
        "aliases": [
            "percentages", "percentage", "percent",
            "percentage problems", "percentage increase", "percentage decrease",
            "successive percentage", "percentage change", "percent problems",
        ],
    },

    "Profit and Loss": {
        "category": "Aptitude",
        "subcategory": "Profit & Loss",
        "ai_context": (
            "Profit and Loss: CP, SP, profit/loss percent, marked price, "
            "discount, successive discounts, dishonest dealer — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "profit and loss", "profit & loss", "profit loss",
            "profit", "loss", "profit percent", "loss percent",
            "discount", "marked price", "selling price", "cost price",
            "successive discounts", "trade discount", "equivalent discount",
            "profit loss problems",
        ],
    },

    "Simple and Compound Interest": {
        "category": "Aptitude",
        "subcategory": "Simple & Compound Interest",
        "ai_context": (
            "Simple Interest (SI = PRT/100) and Compound Interest: "
            "difference, half-yearly/quarterly compounding, effective rate, "
            "depreciation — as tested in placement aptitude exams."
        ),
        "aliases": [
            "simple interest", "compound interest",
            "simple and compound interest", "si ci",
            "si", "ci", "interest problems", "interest",
            "half yearly compounding", "quarterly compounding",
            "effective rate", "population growth", "depreciation",
            "simple interest problems", "compound interest problems",
        ],
    },

    "Time and Work": {
        "category": "Aptitude",
        "subcategory": "Time & Work",
        "ai_context": (
            "Time and Work: combined work rate, LCM method, "
            "pipes and cisterns, work and wages — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "time and work", "work and time", "work problems",
            "work", "efficiency work",
            "pipes and cisterns", "pipes cisterns",
            "pipes", "cisterns", "cistern", "tank filling",
            "tap", "inlet", "outlet pipe",
            "work and wages", "time work problems",
        ],
    },

    "Time Speed Distance": {
        "category": "Aptitude",
        "subcategory": "Time Speed Distance",
        "ai_context": (
            "Time, Speed and Distance: speed = distance/time, relative speed, "
            "average speed, trains crossing (pole, platform), boats and streams "
            "(upstream/downstream), races — as tested in placement aptitude exams."
        ),
        "aliases": [
            "time speed distance", "speed distance time", "speed and distance",
            "speed", "distance time", "tsd",
            "relative speed",
            "trains", "train problems", "train crossing",
            "boats and streams", "boats", "boat", "streams", "stream",
            "upstream", "downstream", "speed of stream", "speed of boat",
            "average speed", "races",
            "time distance", "speed distance",
        ],
    },

    "Boats and Streams": {
        "category": "Aptitude",
        "subcategory": "Boats & Streams",
        "ai_context": (
            "Boats and Streams: speed of boat in still water, speed of current, "
            "upstream speed = boat - current, downstream speed = boat + current, "
            "time calculations, distance problems — as tested in placement aptitude exams."
        ),
        "aliases": [
            "boats and streams", "boats streams", "boat and stream",
            "upstream downstream", "upstream", "downstream",
            "speed of current", "speed of stream", "speed of boat",
            "still water", "boats aptitude", "stream problems",
        ],
    },

    "Trains": {
        "category": "Aptitude",
        "subcategory": "Trains",
        "ai_context": (
            "Train problems: time to cross a pole, platform, another train; "
            "relative speed (same direction, opposite direction), "
            "length of train calculations — as tested in placement aptitude exams."
        ),
        "aliases": [
            "trains", "train problems", "train crossing",
            "train aptitude", "train time", "crossing platform",
            "crossing pole", "two trains", "relative speed trains",
            "length of train",
        ],
    },

    "Pipes and Cisterns": {
        "category": "Aptitude",
        "subcategory": "Pipes & Cisterns",
        "ai_context": (
            "Pipes and Cisterns: inlet pipes, outlet pipes, combined filling time, "
            "leakage problems, fraction of tank filled — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "pipes and cisterns", "pipes cisterns", "cistern",
            "inlet outlet", "pipe problems", "tank problems",
            "filling draining", "leak problem",
        ],
    },

    "Ratio and Proportion": {
        "category": "Aptitude",
        "subcategory": "Ratio & Proportion",
        "ai_context": (
            "Ratio and Proportion: compounded ratio, direct/inverse proportion, "
            "variation, partnership — as tested in placement aptitude exams."
        ),
        "aliases": [
            "ratio and proportion", "ratio proportion", "ratio",
            "proportion", "ratios", "compounded ratio",
            "direct proportion", "inverse proportion", "variation",
            "partnership", "partners",
        ],
    },

    "Mixtures and Alligation": {
        "category": "Aptitude",
        "subcategory": "Mixtures & Alligation",
        "ai_context": (
            "Mixtures and Alligation: alligation method, mixing items of "
            "different prices/concentrations, repeated dilution (milk-water) — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "mixtures and alligation", "mixtures and alligations",
            "mixture", "mixtures", "alligation", "alligations",
            "rule of alligation", "dilution", "milk water problem",
            "mixture problems",
        ],
    },

    "Average": {
        "category": "Aptitude",
        "subcategory": "Average",
        "ai_context": (
            "Average: arithmetic mean, weighted average, average of consecutive numbers, "
            "effect of including/excluding a number — as tested in placement aptitude exams."
        ),
        "aliases": [
            "average", "averages", "mean",
            "weighted average", "average problems",
            "arithmetic mean", "average age",
        ],
    },

    "Permutation and Combination": {
        "category": "Aptitude",
        "subcategory": "Permutations & Combinations",
        "ai_context": (
            "Permutations and Combinations: factorial, nPr, nCr, "
            "circular permutation, word arrangement, selection problems — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "permutation and combination", "permutations and combinations",
            "permutation", "combination", "permutations", "combinations",
            "p and c", "pnc", "p&c",
            "factorial", "npr", "ncr",
            "circular permutation", "word arrangement",
            "selection problems", "arrangement problems",
        ],
    },

    "Probability": {
        "category": "Aptitude",
        "subcategory": "Probability",
        "ai_context": (
            "Probability: classical probability, complementary events, "
            "mutually exclusive, conditional probability, Bayes' theorem, "
            "dice, cards, coins — as tested in placement aptitude exams."
        ),
        "aliases": [
            "probability", "probability problems",
            "classical probability", "conditional probability",
            "bayes theorem", "bayes", "bayes rule",
            "dice", "cards probability", "coins probability",
            "independent events", "mutually exclusive events",
            "sample space",
        ],
    },

    "Problems on Ages": {
        "category": "Aptitude",
        "subcategory": "Problems on Ages",
        "ai_context": (
            "Problems on Ages: present age, past age, future age, "
            "ratio of ages, algebraic equations — as tested in placement aptitude exams."
        ),
        "aliases": [
            "problems on ages", "age problems", "ages",
            "age", "age ratio", "present age", "future age",
        ],
    },

    "Calendar Problems": {
        "category": "Aptitude",
        "subcategory": "Calendar",
        "ai_context": (
            "Calendar Problems: day of the week for a given date, "
            "odd days concept, leap year, Zeller's formula — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "calendar", "calendar problems", "day of week",
            "calendar aptitude", "odd days", "leap year",
            "what day is it", "calendar reasoning",
        ],
    },

    "Clock Problems": {
        "category": "Aptitude",
        "subcategory": "Clocks",
        "ai_context": (
            "Clock Problems: angle between hour and minute hands, "
            "time at which hands coincide, overlap, opposite — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "clock problems", "clocks", "clock", "clock aptitude",
            "clock angles", "hour minute hand", "clock reasoning",
            "clock interview",
        ],
    },

    "Data Interpretation": {
        "category": "Aptitude",
        "subcategory": "Data Interpretation",
        "ai_context": (
            "Data Interpretation: bar charts, pie charts, line graphs, tables, "
            "mixed graphs — as tested in placement aptitude exams."
        ),
        "aliases": [
            "data interpretation", "di", "data interp",
            "bar chart", "bar graph", "pie chart", "pie graph",
            "line graph", "table di", "mixed graph",
            "data sufficiency", "graph interpretation",
        ],
    },

    "Logical Reasoning": {
        "category": "Aptitude",
        "subcategory": "Logical Reasoning",
        "ai_context": (
            "Logical Reasoning: number/letter series, coding-decoding, blood relations, "
            "direction sense, seating arrangement (linear/circular), syllogisms, "
            "puzzles, clock, calendar — as tested in placement aptitude exams."
        ),
        "aliases": [
            "logical reasoning", "lr", "reasoning", "logical",
            "number series", "series", "letter series", "alphanumeric series",
            "coding decoding", "coding-decoding", "coding", "decoding",
            "blood relations", "blood relation", "family tree",
            "direction sense", "direction", "directions",
            "seating arrangement", "seating", "arrangement",
            "circular arrangement", "linear arrangement",
            "syllogism", "syllogisms",
            "puzzles", "puzzle",
            "clock problems", "clock",
            "calendar problems", "calendar",
            "statement conclusion", "statement assumption",
            "analogy", "analogies", "odd one out",
            "input output reasoning", "matrix reasoning",
        ],
    },

    "Partnership": {
        "category": "Aptitude",
        "subcategory": "Partnership",
        "ai_context": (
            "Partnership: simple and compound partnership, "
            "profit/loss sharing among partners — as tested in placement aptitude exams."
        ),
        "aliases": [
            "partnership problems", "partners profit",
            "simple partnership", "compound partnership",
        ],
    },

    "Mensuration": {
        "category": "Aptitude",
        "subcategory": "Mensuration",
        "ai_context": (
            "Mensuration: area and perimeter of 2D shapes (circle, square, rectangle, "
            "triangle), surface area and volume of 3D shapes (cube, cylinder, cone, sphere) "
            "— as tested in placement aptitude exams."
        ),
        "aliases": [
            "mensuration", "area", "perimeter",
            "area and perimeter", "volume", "surface area",
            "2d shapes", "3d shapes", "circle area",
            "triangle area", "sphere volume", "cylinder volume",
            "cone volume", "cube volume",
        ],
    },

    "Trigonometry": {
        "category": "Aptitude",
        "subcategory": "Trigonometry",
        "ai_context": (
            "Trigonometry: sin, cos, tan, identities, heights and distances, "
            "angle of elevation, angle of depression — as tested in placement aptitude exams."
        ),
        "aliases": [
            "trigonometry", "trigo", "trig",
            "sin cos tan", "trigonometric identities",
            "heights and distances", "angle of elevation",
            "angle of depression",
        ],
    },

    "Algebra": {
        "category": "Aptitude",
        "subcategory": "Algebra",
        "ai_context": (
            "Algebra: linear equations, quadratic equations, inequalities, "
            "polynomials, indices/surds — as tested in placement aptitude exams."
        ),
        "aliases": [
            "algebra", "algebraic equations", "linear equations",
            "quadratic equations", "quadratic", "polynomials",
            "inequalities", "indices", "surds",
            "simultaneous equations",
        ],
    },

    # =========================================================================
    # ── VERBAL ────────────────────────────────────────────────────────────────
    # =========================================================================

    "Grammar": {
        "category": "Verbal",
        "subcategory": "Grammar",
        "ai_context": (
            "English Grammar: all 12 tenses, subject-verb agreement, articles, "
            "prepositions, conjunctions, active/passive voice, direct/indirect speech, "
            "conditionals — as tested in placement verbal exams."
        ),
        "aliases": [
            "grammar", "english grammar", "basic grammar", "advanced grammar",
            "tenses", "tense", "all tenses", "12 tenses",
            "subject verb agreement", "sva",
            "articles", "article usage", "a an the",
            "prepositions", "preposition usage",
            "conjunctions", "coordinating conjunctions",
            "active voice", "passive voice", "active passive",
            "direct speech", "indirect speech", "narration",
            "question tags", "tag questions",
            "conditionals", "if clauses",
            "parts of speech", "nouns", "verbs", "adjectives", "adverbs",
            "pronouns", "interjections",
        ],
    },

    "Vocabulary": {
        "category": "Verbal",
        "subcategory": "Synonyms & Antonyms",
        "ai_context": (
            "Vocabulary: synonyms, antonyms, contextual word usage, "
            "one-word substitution, idioms and phrases, commonly confused words, "
            "verbal analogies — as tested in placement verbal exams."
        ),
        "aliases": [
            "vocabulary", "vocab",
            "synonyms", "synonym",
            "antonyms", "antonym",
            "synonyms and antonyms", "synonyms antonyms",
            "one word substitution", "one word",
            "idioms", "idiom", "idioms and phrases", "phrases",
            "word meaning", "word meanings",
            "commonly confused words", "homophones", "homonyms",
            "analogies verbal", "analogy verbal", "verbal analogy",
        ],
    },

    "Reading Comprehension": {
        "category": "Verbal",
        "subcategory": "Reading Comprehension",
        "ai_context": (
            "Reading Comprehension: passage-based questions, main idea, "
            "inference, vocabulary in context, author's tone — "
            "as tested in placement verbal exams."
        ),
        "aliases": [
            "reading comprehension", "rc", "comprehension",
            "passage", "passages", "passage reading",
            "reading passage", "unseen passage",
        ],
    },

    "Sentence Correction": {
        "category": "Verbal",
        "subcategory": "Sentence Correction",
        "ai_context": (
            "Sentence Correction: spotting grammatical errors, sentence improvement, "
            "fill in the blanks, cloze test — as tested in placement verbal exams."
        ),
        "aliases": [
            "sentence correction", "error detection", "error spotting",
            "spot the error", "find the error", "error identification",
            "sentence improvement", "improve the sentence",
            "fill in the blanks", "fill in blanks", "fill in the blank",
            "blanks", "cloze test", "cloze passage",
            "error correction", "grammatical errors",
        ],
    },

    "Para Jumbles": {
        "category": "Verbal",
        "subcategory": "Para Jumbles",
        "ai_context": (
            "Para Jumbles: rearranging jumbled sentences to form a coherent paragraph; "
            "topic sentence, transition words — as tested in placement verbal exams."
        ),
        "aliases": [
            "para jumbles", "para jumble", "paragraph jumbles",
            "jumbled sentences", "sentence rearrangement",
            "sentence order", "rearrange sentences",
            "paragraph formation",
        ],
    },

    "Verbal Reasoning": {
        "category": "Verbal",
        "subcategory": "Verbal Reasoning",
        "ai_context": (
            "Verbal Reasoning: critical reasoning, argument evaluation, "
            "strengthen/weaken arguments, assumption questions, "
            "conclusion questions — as tested in placement verbal exams."
        ),
        "aliases": [
            "verbal reasoning", "critical reasoning",
            "argument evaluation", "strengthen argument",
            "weaken argument", "assumption verbal",
            "conclusion verbal", "verbal ability",
            "verbal reasoning interview",
        ],
    },

    "Soft Skills": {
        "category": "Verbal",
        "subcategory": "Soft Skills",
        "ai_context": (
            "Soft Skills: communication (verbal, non-verbal, written), "
            "group discussion, interpersonal skills, teamwork, leadership, "
            "professional email writing — as tested in placement behavioral rounds."
        ),
        "aliases": [
            "soft skills", "soft", "communication skills",
            "communication", "interpersonal skills",
            "leadership", "teamwork", "group discussion", "gd",
            "professional communication", "email writing",
            "time management", "adaptability", "problem solving skills",
        ],
    },

    # =========================================================================
    # ── HR / BEHAVIORAL INTERVIEW ─────────────────────────────────────────────
    # =========================================================================

    "HR Interview": {
        "category": "Verbal",
        "subcategory": "HR Interview",
        "ai_context": (
            "HR Interview questions: tell me about yourself, strengths and weaknesses, "
            "why this company, where do you see yourself in 5 years, "
            "teamwork experience, conflict resolution, salary negotiation — "
            "as tested in placement HR rounds."
        ),
        "aliases": [
            "hr interview", "hr round", "hr questions",
            "tell me about yourself", "strengths weaknesses",
            "why this company", "behavioral interview",
            "situational interview", "star method",
            "interview questions", "hr preparation",
            "self introduction", "introduce yourself",
            "salary negotiation", "career goals",
        ],
    },

    "Group Discussion": {
        "category": "Verbal",
        "subcategory": "Group Discussion",
        "ai_context": (
            "Group Discussion: GD topics, how to initiate, summarize, "
            "body language, listening skills, current affairs topics — "
            "as tested in placement rounds."
        ),
        "aliases": [
            "group discussion", "gd", "gd topics",
            "gd preparation", "group discussion tips",
            "pi", "personal interview",
        ],
    },

}


# ===========================================================================
# SECTION 2 - BUILD LOOKUP INDEX
# ===========================================================================

_ALIAS_INDEX: Dict[str, str] = {}

for _canon, _meta in CANONICAL_TOPICS.items():
    for _alias in _meta["aliases"]:
        _al = _alias.strip().lower()
        if _al in _ALIAS_INDEX:
            existing = _ALIAS_INDEX[_al]
            if existing != _canon and not existing.startswith("__MULTI__"):
                _ALIAS_INDEX[_al] = f"__MULTI__{existing}||{_canon}"
            elif existing.startswith("__MULTI__") and _canon not in existing:
                _ALIAS_INDEX[_al] = f"{existing}||{_canon}"
        else:
            _ALIAS_INDEX[_al] = _canon


# ===========================================================================
# SECTION 3 - NOISE / REJECTION LIST
# ===========================================================================

_NOISE: set = {
    "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "hello", "hi", "hey", "ok", "okay", "yes", "no", "yep", "nope",
    "sure", "thanks", "thank", "please", "sorry", "bye",
    "what", "how", "why", "when", "where", "who", "which",
    "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "have", "has", "had",
    "can", "could", "will", "would", "shall", "should", "may", "might",
    "good", "bad", "easy", "hard", "difficult", "simple",
    "nice", "great", "best", "worst", "top", "new", "old",
    "big", "small", "large", "fast", "slow", "long", "short",
    "first", "last", "next", "previous", "same", "different",
    "all", "any", "some", "few", "many", "more", "most", "less",
    "up", "down", "in", "out", "on", "off", "at", "to", "for",
    "and", "or", "but", "not", "the", "a", "an", "of", "with",
    "by", "from", "into", "about", "over", "under",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "zero", "hundred", "thousand", "million",
    "test", "quiz", "exam", "question", "answer", "topic",
    "subject", "chapter", "unit", "lesson", "study", "learn",
    "abc", "xyz", "asdf", "qwerty", "aaa", "bbb", "ccc", "zzz",
    "lol", "idk", "omg", "wtf", "lmao", "lmfao",
    "jjj", "kkk", "mmm", "nnn", "ppp", "rrr", "sss", "ttt",
    "list", "problems", "questions", "examples", "notes", "pdf",
    "help", "important", "basic", "advanced", "level",
    "introduction", "overview", "summary", "revision",
    "water", "fire", "air", "earth", "light", "sound", "energy",
    "money", "bank", "house", "road", "bus",
    "book", "pen", "paper", "table", "chair", "door", "window",
    "day", "week", "month", "year", "hour", "minute", "second",
    "man", "woman", "child", "student", "teacher", "doctor",
    "city", "country", "world",
    "color", "colour", "red", "blue", "green", "yellow", "white", "black",
    "run", "go", "come", "make", "take", "give", "get",
    "read", "write", "speak", "listen", "watch", "see",
    "eat", "drink", "sleep", "walk", "talk",
    "normal", "standard", "general", "common", "regular", "special",
    "theory", "method", "approach", "technique", "process", "system",
    "model", "type", "form", "kind", "mode", "style",
    "point", "line", "plane", "surface", "area", "space", "volume",
    "key", "value", "size", "count",
    "food", "meal", "fruit", "animal", "plant",
    "music", "sport", "game", "movie", "film", "art",
    "love", "hate", "feel", "emotion", "happy", "sad",
    "police", "army", "law", "rule", "crime",
    "weather", "rain", "sun", "cloud", "wind", "snow",
    "number", "data", "language", "object", "class", "function",
    "loop", "array", "node", "link", "base", "case", "flow",
    "box", "block", "spring", "load", "force", "motor",
    "heat", "wave", "current", "voltage", "frequency", "signal",
    "pump", "chain", "code", "map", "set", "index",
    "person", "place", "thing", "idea", "part",
    "fact", "side", "hand",
    "right", "left", "front", "back",
    "high", "low", "open", "close",
    "start", "stop", "begin", "end",
    "add", "remove", "delete", "update", "create", "build",
    "find", "search", "check", "try",
    "use", "apply", "call",
}

_NOISE_UNLESS_ALIAS: set = {
    "speed", "stress", "strain", "work", "trains", "boat", "boats",
    "pipes", "sorting", "array", "tree", "graph", "heap", "stack",
    "queue", "cache", "power", "signal", "set", "map", "code",
    "trie", "tries", "dsa", "dp", "bfs", "dfs", "sql", "os",
    "oop", "oops", "api", "git", "jwt", "css", "html",
    "cnn", "rnn", "lstm", "gru",
    "c", "r", "ai", "ml",
}


# ===========================================================================
# SECTION 4 - VALIDITY CHECK
# ===========================================================================

_GIBBERISH_RE = re.compile(r'(.)\1{3,}|^[\W\d]+$', re.I)
_SINGLE_LETTER_TOPICS: set = {"c", "a", "r"}


def _is_valid_query(text: str) -> bool:
    clean = text.strip().lower()

    if not re.search(r'[a-zA-Z]', clean):
        if clean in _ALIAS_INDEX:
            return True
        return False

    if clean in _SINGLE_LETTER_TOPICS:
        return True

    if len(clean) <= 8 and clean in _ALIAS_INDEX:
        return True

    tokens = re.split(r'[\s\-/&,]+', clean)
    if len(tokens) == 1:
        tok = tokens[0].strip('.,;:')
        if tok in _NOISE and tok not in _NOISE_UNLESS_ALIAS:
            return False

    if len(clean.replace(' ', '').replace('+', '').replace('#', '')) < 2:
        return False

    for word in tokens:
        word = word.strip('.,;:')
        if len(word) <= 2:
            continue
        if _GIBBERISH_RE.search(word):
            return False
        letters = [c for c in word if c.isalpha()]
        if len(letters) > 5:
            vowels = sum(1 for c in letters if c in 'aeiou')
            if vowels / len(letters) < 0.08:
                return False

    return True


# ===========================================================================
# SECTION 5 - FUZZY SCORE HELPER
# ===========================================================================

def _fuzzy_score(a: str, b: str) -> float:
    """Bigram-based Dice coefficient similarity. Returns 0.0–1.0."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    def bigrams(s: str) -> List[str]:
        return [s[i:i + 2] for i in range(len(s) - 1)] if len(s) >= 2 else list(s)

    a_bg = bigrams(a)
    b_bg = bigrams(b)

    if not a_bg or not b_bg:
        return 0.0

    b_copy = b_bg[:]
    common = 0
    for bg in a_bg:
        if bg in b_copy:
            common += 1
            b_copy.remove(bg)

    return (2.0 * common) / (len(a_bg) + len(b_bg))


def _best_fuzzy_match(query: str) -> tuple:
    """Scan entire alias index and return (best_canonical, best_score)."""
    q_len = len(query)
    best_canon = None
    best_score = 0.0

    for alias, canon in _ALIAS_INDEX.items():
        a_len = len(alias)
        if a_len == 0 or q_len == 0:
            continue
        ratio = a_len / q_len
        if ratio < 0.4 or ratio > 2.5:
            continue

        score = _fuzzy_score(query, alias)
        if score > best_score:
            best_score = score
            best_canon = canon

    if best_canon and best_canon.startswith("__MULTI__"):
        parts = [c for c in best_canon[len("__MULTI__"):].split("||") if c in CANONICAL_TOPICS]
        best_canon = parts[0] if parts else None

    return best_canon, best_score


# ===========================================================================
# SECTION 6 - CORE RESOLVER
# ===========================================================================

def _make_result(canonical: str) -> dict:
    meta = CANONICAL_TOPICS[canonical]
    return {
        "status":        "single",
        "topic":         meta["subcategory"],
        "canonical":     canonical,
        "subtopic":      "",
        "category":      meta["category"],
        "ai_context":    meta["ai_context"],
        "display_label": canonical,
    }


def resolve_topic(user_input: str) -> dict:
    """
    Resolve user search query → canonical placement topic.

    Returns one of:
        { status:'single',  topic, canonical, subtopic, category, ai_context, display_label }
        { status:'multi',   options:[...], query }
        { status:'new',     topic, category, ai_context }
        { status:'invalid', message }
    """
    raw   = user_input.strip()
    clean = re.sub(r'\s+', ' ', raw.lower()).strip()

    # ── Basic length / noise guard ────────────────────────────────────────
    if not _is_valid_query(clean):
        if len(clean.replace(' ', '')) < 2:
            return {"status": "invalid", "message": "Please type at least 2 characters."}
        return {
            "status":  "invalid",
            "message": (
                f'"{raw}" is not a recognised placement topic. '
                'Try something like "dynamic programming", "SQL joins", '
                '"boats and streams", or "reading comprehension".'
            ),
        }

    # ── 1. Exact alias match ──────────────────────────────────────────────
    hit = _ALIAS_INDEX.get(clean)
    if hit:
        if hit.startswith("__MULTI__"):
            canons = [c for c in hit[len("__MULTI__"):].split("||")
                      if c in CANONICAL_TOPICS]
            options = [_make_result(c) for c in canons]
            return {"status": "multi", "options": options, "query": raw}
        return _make_result(hit)

    # ── 2. Prefix match (min 3 chars) ─────────────────────────────────────
    if len(clean) >= 3:
        prefix_hits: List[str] = []
        seen: set = set()
        for alias, canon in _ALIAS_INDEX.items():
            if not alias.startswith(clean):
                continue
            entries = ([c for c in canon[len("__MULTI__"):].split("||")]
                       if canon.startswith("__MULTI__") else [canon])
            for c in entries:
                if c not in seen and c in CANONICAL_TOPICS:
                    prefix_hits.append(c)
                    seen.add(c)

        if len(prefix_hits) == 1:
            return _make_result(prefix_hits[0])
        if len(prefix_hits) > 1:
            options = [_make_result(c) for c in prefix_hits]
            return {"status": "multi", "options": options, "query": raw}

    # ── 3. Substring match (min 4 chars) ──────────────────────────────────
    if len(clean) >= 4:
        sub_hits: List[str] = []
        seen2: set = set()
        for alias, canon in _ALIAS_INDEX.items():
            if clean not in alias:
                continue
            entries = ([c for c in canon[len("__MULTI__"):].split("||")]
                       if canon.startswith("__MULTI__") else [canon])
            for c in entries:
                if c not in seen2 and c in CANONICAL_TOPICS:
                    sub_hits.append(c)
                    seen2.add(c)

        if len(sub_hits) == 1:
            return _make_result(sub_hits[0])
        if len(sub_hits) > 1:
            options = [_make_result(c) for c in sub_hits]
            return {"status": "multi", "options": options, "query": raw}

    # ── 4. Fuzzy match — catch typos ──────────────────────────────────────
    best_canon, best_score = _best_fuzzy_match(clean)

    if best_score >= 0.75 and best_canon and best_canon in CANONICAL_TOPICS:
        return _make_result(best_canon)

    if best_score >= 0.55 and best_canon and best_canon in CANONICAL_TOPICS:
        suggested = CANONICAL_TOPICS[best_canon]["subcategory"]
        return {
            "status": "invalid",
            "message": (
                f'"{raw}" doesn\'t match any topic. '
                f'Did you mean "{suggested}"?'
            ),
        }

    # ── 5. Reject short single-word queries that matched nothing ──────────
    words = clean.split()
    total_chars = len(clean.replace(' ', ''))

    if len(words) == 1 and total_chars <= 6:
        return {
            "status":  "invalid",
            "message": (
                f'"{raw}" is not a recognised placement topic. '
                'Try something like "dynamic programming", "SQL joins", or "probability".'
            ),
        }

    # ── 6. Reject all-gibberish words ─────────────────────────────────────
    gibberish_words = 0
    for w in words:
        letters = [c for c in w if c.isalpha()]
        if len(letters) >= 3:
            vowels = sum(1 for c in letters if c in 'aeiouAEIOU')
            if vowels == 0:
                gibberish_words += 1
    if len(words) > 0 and gibberish_words >= len(words):
        return {
            "status":  "invalid",
            "message": f'"{raw}" doesn\'t look like a valid topic. Please check your spelling.',
        }

    # ── 7. Allow as NEW topic if it contains real-looking words ───────────
    has_real_word = False
    for w in words:
        letters = [c for c in w if c.isalpha()]
        if len(letters) >= 3:
            vowels = sum(1 for c in letters if c in 'aeiouAEIOU')
            if vowels / len(letters) >= 0.15:
                has_real_word = True
                break

    if not has_real_word:
        return {
            "status":  "invalid",
            "message": f'"{raw}" doesn\'t look like a valid topic. Please check your spelling.',
        }

    title_cased = raw.title()
    return {
        "status":     "new",
        "topic":      title_cased,
        "category":   "Technical",
        "ai_context": (
            f"{title_cased} — core concepts, theory, and applied problems "
            f"as tested in engineering placement exams and technical interviews."
        ),
    }


# ===========================================================================
# SECTION 7 - AI CONTEXT BUILDER
# ===========================================================================

def build_ai_context(topic: str, subtopic: str, ai_context: str = '') -> str:
    if ai_context:
        first_word = subtopic.split()[0] if subtopic else topic.split()[0]
        return (
            f"Topic: {topic}\n"
            f"Subtopic: {subtopic}\n"
            f"Context: Generate questions ONLY about: {ai_context}\n"
            f"Do NOT generate questions about the literal/everyday meaning of "
            f'"{first_word}" — focus strictly on the placement exam context above.'
        )
    return f"Topic: {topic}\nSubtopic: {subtopic if subtopic else topic}"


# ===========================================================================
# SECTION 8 - QUICK STATS
# ===========================================================================

if __name__ == "__main__":
    print(f"Total canonical topics: {len(CANONICAL_TOPICS)}")
    print(f"Total aliases indexed:  {len(_ALIAS_INDEX)}")

    cats = {}
    for v in CANONICAL_TOPICS.values():
        cats[v['category']] = cats.get(v['category'], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count} topics")

    # Quick tests
    tests = [
        "langchain", "rag", "mlops", "hugging face", "transformers",
        "nextjs", "fastapi", "flutter", "react native", "android",
        "boats", "trains", "clocks", "calendar", "hr interview",
        "group discussion", "gd", "redis", "mongodb",
        "linear algebra", "calculus", "statistics",
        "competitive programming", "competitive coding",
        "software testing", "selenium", "junit",
        "linux", "bash scripting",
        "azure", "gcp", "graphql",
        "pyhton", "javascrip", "machne learning",
    ]

    print("\n--- Quick Tests ---")
    for q in tests:
        r = resolve_topic(q)
        st = r['status']
        if st == 'single':
            print(f"  '{q}' → {r['canonical']}")
        elif st == 'multi':
            print(f"  '{q}' → MULTI: {[o['canonical'] for o in r['options'][:2]]}")
        elif st == 'new':
            print(f"  '{q}' → NEW: {r['topic']}")
        else:
            print(f"  '{q}' → INVALID: {r['message'][:60]}")