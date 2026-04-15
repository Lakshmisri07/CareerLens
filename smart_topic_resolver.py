"""
smart_topic_resolver.py  –  v6.0
==================================
Complete overhaul:
  • 1000+ topics across ALL branches: CSE/IT/ECE/EEE/MECH/CIVIL/CHEM/AI-ML
  • All popular tech stacks covered (React, Flask, Node, Docker, etc.)
  • Industry-relevant topics outside curriculum (for placement prep)
  • Exhaustive alias lists per topic
  • Strict noise/rejection list: real English words that are NOT topics
  • Fuzzy matching to catch typos (e.g. "pyhton" → Python, "java scrop" → INVALID)
  • resolve_topic() returns category for frontend routing
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
            "dataclass", "type hints python",
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
            "js interview", "javascript interview",
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
            "tsc", "tsconfig",
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
            "go concurrency", "go routines", "go modules",
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
            "kotlin basics", "kotlin language",
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
            "swiftui", "swift ios", "xcode swift",
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
            "ownership rust", "borrowing rust", "cargo rust",
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
            "php oop", "php mysql", "php web",
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
            "ror", "ruby rails",
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
            "functional scala",
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
            "sql index", "sql optimization",
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
            "linked list operations",
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
            "min stack", "max stack",
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
            "n ary tree", "trie data structure",
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
            "union find", "disjoint set", "dsu",
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
            "bsearch",
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
            "mutual recursion",
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
            "relational database", "database systems",
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
            "computer networking", "network concepts",
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
            "access modifiers",
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
            "media queries", "css animations", "html forms",
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
            "angular 4", "angular 8", "angular 12", "angular 15",
            "ng", "rxjs", "angular services", "angular routing",
            "angular directives", "angular pipes",
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
            "options api vue",
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
            "rest api node", "middleware express",
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
            "django authentication", "django forms",
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
            "spring rest", "spring microservices",
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
            "graphql", "grpc",
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
            "laravel", "next.js", "nextjs", "nuxt.js",
            "gatsby", "svelte", "fastapi",
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
            "virtualization", "hypervisor",
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
            "dynamodb aws", "elasticache",
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
            "docker volumes", "docker networking",
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
            "helm", "kubernetes cluster",
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
            "logging", "elk stack", "splunk",
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
            "owasp", "owasp top 10",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Machine Learning / AI / Data Science ─────────────────────
    # =========================================================================

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
            "flink", "kafka streaming",
        ],
    },

    # =========================================================================
    # ── TECHNICAL ─ Compiler Design ───────────────────────────────────────────
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
    # ── TECHNICAL ─ CHEMICAL Topics ───────────────────────────────────────────
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

    "Augmented and Virtual Reality": {
        "category": "Technical",
        "subcategory": "AR/VR",
        "ai_context": (
            "AR/VR: AR vs VR vs MR, OpenXR, Unity, Unreal Engine, "
            "HMD devices, spatial computing — as tested in placement exams."
        ),
        "aliases": [
            "ar vr", "augmented reality", "virtual reality",
            "mixed reality", "xr", "metaverse", "unity 3d", "unreal engine",
        ],
    },
    "Preprocessor and Macros": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "C Preprocessor: #define, #include, #ifdef/#ifndef, #pragma, "
            "macro functions, stringization, token pasting, include guards — "
            "as tested in placement exams."
        ),
        "aliases": [
            "preprocessor", "c preprocessor", "macros", "macro", "#define",
            "include guard", "header files", "c macros", "pragma",
            "conditional compilation", "preprocessor directives",
        ],
    },
 
    "Dynamic Memory Allocation": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "Dynamic Memory in C: malloc, calloc, realloc, free, memory leaks, "
            "dangling pointers, heap vs stack — as tested in placement exams."
        ),
        "aliases": [
            "dynamic memory", "dynamic memory allocation", "malloc", "calloc",
            "realloc", "free", "heap memory", "memory leak",
            "dangling pointer", "memory allocation c",
        ],
    },
 
    "String Handling in C": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "C String functions: strlen, strcpy, strcat, strcmp, strstr, "
            "strtok, sprintf, sscanf, string arrays — as tested in placement exams."
        ),
        "aliases": [
            "string handling", "c strings", "string functions c",
            "strlen", "strcpy", "strcat", "strcmp", "strstr", "strtok",
            "string manipulation c", "char array",
        ],
    },
 
    "File Handling in C": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "C File I/O: fopen, fclose, fread, fwrite, fprintf, fscanf, fseek, ftell, "
            "rewind, binary vs text mode, EOF — as tested in placement exams."
        ),
        "aliases": [
            "file handling c", "file i/o c", "fopen", "fclose",
            "fread fwrite", "fprintf", "fscanf",
            "binary file", "text file c", "file operations c",
        ],
    },
 
    "C++ STL": {
        "category": "Technical",
        "subcategory": "C++",
        "ai_context": (
            "C++ Standard Template Library: vector, list, deque, set, multiset, "
            "map, multimap, unordered_map, unordered_set, stack, queue, "
            "priority_queue, algorithms (sort, find, binary_search), iterators — "
            "as tested in placement exams."
        ),
        "aliases": [
            "stl", "c++ stl", "standard template library",
            "vector stl", "map stl", "set stl", "deque stl",
            "stl algorithms", "stl containers", "stl iterators",
            "unordered map", "unordered set", "multimap", "multiset",
            "priority queue stl", "c++ containers",
        ],
    },
 
    "C++ Multithreading": {
        "category": "Technical",
        "subcategory": "C++",
        "ai_context": (
            "C++ Multithreading: std::thread, mutex, lock_guard, unique_lock, "
            "condition_variable, atomic, async, future, promise — "
            "as tested in placement exams."
        ),
        "aliases": [
            "c++ multithreading", "c++ threads", "std thread",
            "mutex c++", "lock guard", "condition variable c++",
            "atomic c++", "c++ concurrency", "thread safety c++",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Java (missing subtopics) ──────────────────────────────────
# =========================================================================
 
    "Java Collections Framework": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java Collections: List (ArrayList, LinkedList, Vector), "
            "Set (HashSet, TreeSet, LinkedHashSet), "
            "Map (HashMap, TreeMap, LinkedHashMap, Hashtable), "
            "Queue, Deque, Collections utility class — as tested in placement exams."
        ),
        "aliases": [
            "java collections", "collections framework", "java list",
            "arraylist", "linkedlist java", "hashset", "treeset",
            "hashmap", "treemap", "linkedhashmap",
            "java queue", "java deque", "java stack",
            "collections utility", "iterator java",
            "comparable", "comparator java",
        ],
    },
 
    "Java Multithreading": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java Multithreading: Thread class, Runnable, synchronized, "
            "volatile, wait/notify/notifyAll, ExecutorService, "
            "CountDownLatch, Semaphore, ReentrantLock — as tested in placement exams."
        ),
        "aliases": [
            "java multithreading", "java threads", "thread java",
            "runnable java", "synchronized java", "volatile java",
            "wait notify", "executor service", "thread pool java",
            "countdownlatch", "cyclicbarrier", "semaphore java",
            "reentrantlock", "java concurrent", "java concurrency",
        ],
    },
 
    "Java 8 Features": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java 8: lambda expressions, functional interfaces, Stream API, "
            "Optional class, default/static methods in interfaces, "
            "method references, Date/Time API — as tested in placement exams."
        ),
        "aliases": [
            "java 8", "java 8 features", "lambda java", "stream api",
            "java streams", "functional interface", "optional java",
            "method reference java", "java lambda", "java stream",
            "collectors java", "filter map reduce java",
            "java date time", "localdate", "localdatetime",
        ],
    },
 
    "JDBC": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "JDBC: DriverManager, Connection, Statement, PreparedStatement, "
            "CallableStatement, ResultSet, CRUD operations, transactions — "
            "as tested in placement exams."
        ),
        "aliases": [
            "jdbc", "java database connectivity", "jdbc connection",
            "preparedstatement", "resultset", "jdbc crud",
            "jdbc transaction", "connection pooling",
        ],
    },
 
    "Java Design Patterns": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java Design Patterns: Singleton, Factory, Abstract Factory, "
            "Builder, Prototype, Adapter, Facade, Decorator, Observer, "
            "Strategy, Command, Iterator, Template Method — "
            "as tested in placement exams."
        ),
        "aliases": [
            "java design patterns", "design patterns java",
            "singleton java", "factory java", "builder java",
            "observer java", "strategy java", "decorator java",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Python (missing subtopics) ────────────────────────────────
# =========================================================================
 
    "Python OOP": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python OOP: classes, objects, __init__, self, inheritance, "
            "multiple inheritance, MRO, super(), dunder methods (__str__, "
            "__repr__, __len__, __eq__), @property, @classmethod, "
            "@staticmethod — as tested in placement exams."
        ),
        "aliases": [
            "python oop", "python oops", "python classes", "python objects",
            "python inheritance", "python multiple inheritance",
            "python dunder", "magic methods python", "python mro",
            "python property", "classmethod", "staticmethod python",
            "python __init__", "python self",
        ],
    },
 
    "Python Decorators and Generators": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python Decorators: function decorators, class decorators, "
            "functools.wraps, chaining decorators; "
            "Generators: yield, generator expressions, send(), throw(), "
            "itertools — as tested in placement exams."
        ),
        "aliases": [
            "python decorators", "python generators", "yield python",
            "generator expression", "python yield", "functools",
            "python itertools", "python coroutines basics",
            "decorator pattern python", "generator function",
        ],
    },
 
    "Python Async Programming": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python Async: asyncio, async/await, event loop, coroutines, "
            "tasks, aiohttp, concurrent.futures — as tested in placement exams."
        ),
        "aliases": [
            "python asyncio", "python async await", "python async",
            "async python", "coroutines python", "event loop python",
            "python concurrency", "aiohttp",
        ],
    },
 
    "Python Regular Expressions": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python re module: patterns, match, search, findall, sub, "
            "groups, lookahead/lookbehind, special characters — "
            "as tested in placement exams."
        ),
        "aliases": [
            "python regex", "python regular expressions", "re module",
            "python re", "regex python", "pattern matching python",
            "python search replace regex",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ JavaScript / Web (missing) ────────────────────────────────
# =========================================================================
 
    "JavaScript Advanced Concepts": {
        "category": "Technical",
        "subcategory": "JavaScript",
        "ai_context": (
            "Advanced JS: prototype chain, closures, currying, memoization, "
            "WeakMap/WeakSet, Symbol, Proxy, Reflect, generator functions, "
            "Intersection Observer, Web Workers — as tested in placement exams."
        ),
        "aliases": [
            "javascript advanced", "js advanced", "currying javascript",
            "memoization js", "prototype javascript", "prototype chain js",
            "weakmap", "weakset", "symbol js", "proxy javascript",
            "reflect javascript", "generator js", "web workers",
        ],
    },
 
    "Browser APIs and Web Storage": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "Browser APIs: localStorage, sessionStorage, IndexedDB, Cookies, "
            "Geolocation API, Web Workers, Service Workers, Fetch API, "
            "WebSockets, WebRTC basics — as tested in placement exams."
        ),
        "aliases": [
            "localstorage", "sessionstorage", "web storage",
            "browser storage", "indexeddb", "cookies javascript",
            "geolocation api", "service workers",
            "fetch api", "websockets", "webrtc",
            "browser apis", "web apis",
        ],
    },
 
    "CSS Preprocessors and Frameworks": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "CSS Preprocessors: SASS/SCSS (variables, nesting, mixins, extends), "
            "LESS; CSS Frameworks: Bootstrap (grid, components), Tailwind CSS — "
            "as tested in placement exams."
        ),
        "aliases": [
            "sass", "scss", "less css", "css preprocessor",
            "bootstrap", "tailwind", "tailwind css",
            "bootstrap grid", "css variables", "css custom properties",
            "css modules", "styled components",
        ],
    },
 
    "Next.js": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "Next.js: SSR, SSG, ISR, App Router, pages directory, "
            "getServerSideProps, getStaticProps, API routes, middleware, "
            "Image optimization — as tested in placement exams."
        ),
        "aliases": [
            "next.js", "nextjs", "next js",
            "server side rendering", "static site generation",
            "ssr", "ssg", "isr", "app router", "pages router",
            "getserversideprops", "getstaticprops",
        ],
    },
 
    "FastAPI": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "FastAPI: path operations, Pydantic models, dependency injection, "
            "async support, authentication, OpenAPI docs — as tested in placement exams."
        ),
        "aliases": [
            "fastapi", "fast api", "python fastapi",
            "fastapi pydantic", "fastapi async", "fastapi authentication",
        ],
    },
 
    "GraphQL": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "GraphQL: queries, mutations, subscriptions, schema definition, "
            "resolvers, Apollo Client/Server, DataLoader — "
            "as tested in placement exams."
        ),
        "aliases": [
            "graphql", "graph ql", "graphql queries", "graphql mutations",
            "graphql schema", "apollo graphql", "graphql subscriptions",
            "graphql vs rest",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ DSA (missing specific topics) ─────────────────────────────
# =========================================================================
 
    "Matrix and 2D Arrays": {
        "category": "Technical",
        "subcategory": "Matrix",
        "ai_context": (
            "Matrix problems: matrix rotation, transpose, spiral order, "
            "search in sorted matrix, matrix multiplication, "
            "diagonal traversal — as tested in placement exams."
        ),
        "aliases": [
            "matrix", "2d array", "matrix problems", "matrix rotation",
            "matrix traversal", "spiral matrix", "transpose matrix",
            "search matrix", "matrix multiplication",
        ],
    },
 
    "String Algorithms": {
        "category": "Technical",
        "subcategory": "String Algorithms",
        "ai_context": (
            "String Algorithms: KMP, Rabin-Karp, Z-algorithm, Manacher's algorithm, "
            "longest palindromic substring, anagram detection, string hashing — "
            "as tested in placement exams."
        ),
        "aliases": [
            "string algorithms", "kmp algorithm", "kmp",
            "knuth morris pratt", "rabin karp", "z algorithm",
            "manacher algorithm", "palindrome problems",
            "string matching", "pattern matching string",
            "anagram", "string hashing",
        ],
    },
 
    "Union Find / Disjoint Set": {
        "category": "Technical",
        "subcategory": "Union Find",
        "ai_context": (
            "Union-Find (Disjoint Set Union): union by rank, path compression, "
            "find, union operations, applications in Kruskal's MST, "
            "detecting cycles — as tested in placement exams."
        ),
        "aliases": [
            "union find", "disjoint set", "dsu", "union find algorithm",
            "path compression", "union by rank",
            "disjoint set union", "find union",
        ],
    },
 
    "Segment Trees and Fenwick Trees": {
        "category": "Technical",
        "subcategory": "Advanced Trees",
        "ai_context": (
            "Segment Tree: range queries, point/range updates, lazy propagation; "
            "Fenwick Tree (BIT): prefix sums, range updates — "
            "as tested in placement exams."
        ),
        "aliases": [
            "segment tree", "fenwick tree", "bit tree",
            "binary indexed tree", "range query", "lazy propagation",
            "segment tree problems", "range sum query",
        ],
    },
 
    "Two Pointers and Prefix Sum": {
        "category": "Technical",
        "subcategory": "Techniques",
        "ai_context": (
            "Two Pointers: pair sum, triplet sum, container with most water; "
            "Prefix Sum: subarray sum, range sum queries, 2D prefix sum — "
            "as tested in placement exams."
        ),
        "aliases": [
            "prefix sum", "two pointers prefix", "subarray sum",
            "range sum", "prefix array", "cumulative sum",
            "kadane algorithm", "maximum subarray",
        ],
    },
 
    "Number Theory Algorithms": {
        "category": "Technical",
        "subcategory": "Number Theory",
        "ai_context": (
            "Number Theory: Sieve of Eratosthenes, GCD/LCM (Euclidean algorithm), "
            "modular arithmetic, modular exponentiation, Euler's totient, "
            "Chinese Remainder Theorem — as tested in placement exams."
        ),
        "aliases": [
            "number theory algorithms", "sieve of eratosthenes", "sieve",
            "euclidean algorithm", "gcd algorithm", "lcm algorithm",
            "modular arithmetic", "modular exponentiation",
            "euler totient", "chinese remainder theorem", "crt",
            "prime sieve", "fast exponentiation",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ DBMS (missing) ────────────────────────────────────────────
# =========================================================================
 
    "PL/SQL and Stored Procedures": {
        "category": "Technical",
        "subcategory": "PL/SQL",
        "ai_context": (
            "PL/SQL: blocks (DECLARE, BEGIN, EXCEPTION, END), variables, "
            "cursors (implicit/explicit), procedures, functions, "
            "triggers, packages — as tested in placement exams."
        ),
        "aliases": [
            "pl/sql", "plsql", "stored procedures", "stored procedure",
            "cursors sql", "pl sql", "oracle plsql",
            "triggers sql", "database functions", "sql packages",
            "database procedures",
        ],
    },
 
    "Database Design": {
        "category": "Technical",
        "subcategory": "Database Design",
        "ai_context": (
            "Database Design: conceptual, logical, physical design; "
            "keys (primary, foreign, candidate, super, composite), "
            "referential integrity, denormalization, data modeling — "
            "as tested in placement exams."
        ),
        "aliases": [
            "database design", "db design", "data modeling",
            "primary key", "foreign key", "candidate key",
            "super key", "composite key", "referential integrity",
            "denormalization", "database schema design",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ OS (missing) ──────────────────────────────────────────────
# =========================================================================
 
    "Disk Scheduling": {
        "category": "Technical",
        "subcategory": "Disk Scheduling",
        "ai_context": (
            "Disk Scheduling: FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK; "
            "seek time, rotational latency, access time — "
            "as tested in placement exams."
        ),
        "aliases": [
            "disk scheduling", "disk scheduling algorithms",
            "sstf", "scan disk", "c-scan disk", "look algorithm",
            "seek time", "rotational latency",
            "disk access time", "fcfs disk",
        ],
    },
 
    "Shell Scripting": {
        "category": "Technical",
        "subcategory": "Shell Scripting",
        "ai_context": (
            "Shell Scripting: bash scripts, variables, conditionals (if/elif/else), "
            "loops (for/while/until), functions, arrays, "
            "pipes, redirection, cron jobs — as tested in placement exams."
        ),
        "aliases": [
            "shell scripting", "bash scripting", "bash script",
            "shell script", "linux scripting",
            "bash variables", "bash loops", "bash functions",
            "cron job", "shell commands", "bash commands",
            "linux commands", "shell programming",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Computer Networks (missing) ───────────────────────────────
# =========================================================================
 
    "Data Link Layer": {
        "category": "Technical",
        "subcategory": "Data Link Layer",
        "ai_context": (
            "Data Link Layer: framing, error detection (CRC, checksum, parity), "
            "error correction (Hamming), flow control (sliding window, stop-and-wait), "
            "MAC protocols (CSMA/CD, CSMA/CA), Ethernet, HDLC — "
            "as tested in placement exams."
        ),
        "aliases": [
            "data link layer", "dll", "mac layer",
            "framing", "crc", "cyclic redundancy check",
            "hamming code", "error detection correction",
            "sliding window protocol", "stop and wait",
            "go back n", "selective repeat",
            "csma cd", "csma ca", "mac protocols",
            "ethernet protocol", "aloha", "hdlc",
        ],
    },
 
    "Wireless Networks": {
        "category": "Technical",
        "subcategory": "Wireless Networks",
        "ai_context": (
            "Wireless Networks: IEEE 802.11 (Wi-Fi), Bluetooth, Zigbee, "
            "WiMAX, mobile networks (2G/3G/4G/5G), handoff, WLAN security — "
            "as tested in placement exams."
        ),
        "aliases": [
            "wireless networks", "wifi", "wi-fi", "ieee 802.11",
            "bluetooth", "zigbee", "wimax",
            "wireless security", "wlan", "wpan",
            "mobile networks", "handoff", "roaming",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Software Engineering (missing) ────────────────────────────
# =========================================================================
 
    "Software Testing": {
        "category": "Technical",
        "subcategory": "Software Testing",
        "ai_context": (
            "Software Testing: unit testing, integration testing, system testing, "
            "acceptance testing, regression testing, black-box vs white-box, "
            "equivalence partitioning, boundary value analysis, "
            "mutation testing, TDD, BDD — as tested in placement exams."
        ),
        "aliases": [
            "software testing", "testing", "unit testing", "integration testing",
            "system testing", "acceptance testing", "regression testing",
            "black box testing", "white box testing", "grey box testing",
            "tdd", "bdd", "test driven development",
            "equivalence partitioning", "boundary value analysis",
            "selenium", "junit", "pytest testing", "jest testing",
            "mock testing", "stub", "test coverage",
        ],
    },
 
    "Agile and Scrum": {
        "category": "Technical",
        "subcategory": "Agile",
        "ai_context": (
            "Agile Methodology: Scrum (sprints, ceremonies, roles), Kanban, "
            "XP, SAFe; user stories, story points, velocity, "
            "retrospectives — as tested in placement exams."
        ),
        "aliases": [
            "agile", "scrum", "agile methodology", "scrum framework",
            "kanban", "sprint", "user stories", "story points",
            "product backlog", "sprint backlog", "daily standup",
            "scrum master", "product owner", "velocity agile",
            "retrospective", "agile ceremonies", "scaled agile",
            "safe agile", "extreme programming", "xp agile",
        ],
    },
 
    "Version Control Git": {
        "category": "Technical",
        "subcategory": "Git",
        "ai_context": (
            "Git: init, clone, add, commit, push, pull, fetch, merge, rebase, "
            "cherry-pick, stash, reset (soft/mixed/hard), revert, "
            "branching strategies (GitFlow, trunk-based), conflicts — "
            "as tested in placement exams."
        ),
        "aliases": [
            "git", "version control", "git commands",
            "git merge", "git rebase", "git branching",
            "git stash", "git reset", "git revert",
            "git cherry pick", "gitflow", "trunk based development",
            "merge conflict", "pull request", "code review git",
            "github", "gitlab", "bitbucket",
        ],
    },
 
    "Clean Code and SOLID": {
        "category": "Technical",
        "subcategory": "Clean Code",
        "ai_context": (
            "Clean Code: naming conventions, DRY, KISS, YAGNI; "
            "SOLID: Single Responsibility, Open/Closed, Liskov Substitution, "
            "Interface Segregation, Dependency Inversion — "
            "as tested in placement exams."
        ),
        "aliases": [
            "clean code", "solid principles", "solid",
            "dry principle", "kiss principle", "yagni",
            "single responsibility", "open closed",
            "liskov substitution", "interface segregation",
            "dependency inversion", "refactoring", "code quality",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Cloud / DevOps (missing) ──────────────────────────────────
# =========================================================================
 
    "Linux and Unix": {
        "category": "Technical",
        "subcategory": "Linux",
        "ai_context": (
            "Linux: file system hierarchy, permissions (chmod, chown), "
            "process management (ps, top, kill), networking commands, "
            "package managers (apt, yum), systemd, vim/nano — "
            "as tested in placement exams."
        ),
        "aliases": [
            "linux", "unix", "linux commands", "unix commands",
            "linux file system", "chmod", "chown", "permissions linux",
            "linux processes", "ps aux", "top command",
            "grep", "awk", "sed", "find command",
            "linux networking", "ifconfig", "netstat",
            "apt", "yum", "rpm", "dpkg",
            "systemd", "cron linux", "vim", "nano",
            "bash", "shell linux", "terminal",
        ],
    },
 
    "Networking Commands and Tools": {
        "category": "Technical",
        "subcategory": "Networking Tools",
        "ai_context": (
            "Networking tools: ping, traceroute, nslookup, dig, netstat, "
            "tcpdump, Wireshark, curl, wget, ssh, scp, ftp — "
            "as tested in placement exams."
        ),
        "aliases": [
            "networking commands", "ping", "traceroute", "tracert",
            "nslookup", "dig command", "netstat", "tcpdump",
            "wireshark", "curl", "wget", "ssh", "scp",
            "network troubleshooting", "network tools",
        ],
    },
 
    "CI/CD Pipelines": {
        "category": "Technical",
        "subcategory": "CI/CD",
        "ai_context": (
            "CI/CD: continuous integration, continuous delivery, continuous deployment, "
            "Jenkins pipelines (Jenkinsfile), GitHub Actions (workflows, actions), "
            "GitLab CI (stages, jobs), Docker in CI, automated testing — "
            "as tested in placement exams."
        ),
        "aliases": [
            "ci cd", "ci/cd", "continuous integration", "continuous deployment",
            "continuous delivery", "jenkins pipeline", "jenkinsfile",
            "github actions workflow", "gitlab ci cd", "circle ci",
            "travis ci", "azure devops", "bamboo",
            "automated deployment", "pipeline stages",
        ],
    },
 
    "Microservices Architecture": {
        "category": "Technical",
        "subcategory": "Microservices",
        "ai_context": (
            "Microservices: service decomposition, inter-service communication "
            "(REST, gRPC, message queues), service discovery, API gateway, "
            "circuit breaker, saga pattern, event-driven architecture — "
            "as tested in placement exams."
        ),
        "aliases": [
            "microservices", "microservice architecture",
            "service discovery", "api gateway microservices",
            "circuit breaker", "saga pattern",
            "event driven", "event driven architecture",
            "grpc", "message broker", "service mesh",
            "istio", "consul", "netflix eureka",
        ],
    },
 
    "Infrastructure as Code": {
        "category": "Technical",
        "subcategory": "IaC",
        "ai_context": (
            "Infrastructure as Code: Terraform (providers, resources, state, modules), "
            "Ansible (playbooks, roles, inventory), "
            "CloudFormation, Pulumi — as tested in placement exams."
        ),
        "aliases": [
            "infrastructure as code", "iac", "terraform",
            "terraform providers", "terraform modules", "terraform state",
            "ansible", "ansible playbook", "ansible roles",
            "cloudformation", "pulumi", "chef", "puppet",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Databases (missing) ───────────────────────────────────────
# =========================================================================
 
    "Redis and Caching": {
        "category": "Technical",
        "subcategory": "Redis",
        "ai_context": (
            "Redis: data structures (strings, hashes, lists, sets, sorted sets), "
            "caching patterns (cache-aside, write-through, write-behind), "
            "TTL, pub/sub, Redis Cluster, eviction policies — "
            "as tested in placement exams."
        ),
        "aliases": [
            "redis", "redis caching", "redis data structures",
            "redis pub sub", "redis cluster", "redis eviction",
            "cache invalidation", "caching strategies",
            "write through", "cache aside", "write behind",
            "redis sorted sets", "redis hashes",
        ],
    },
 
    "Elasticsearch": {
        "category": "Technical",
        "subcategory": "Elasticsearch",
        "ai_context": (
            "Elasticsearch: inverted index, documents, indices, shards, replicas, "
            "queries (match, term, bool, range), aggregations, Kibana — "
            "as tested in placement exams."
        ),
        "aliases": [
            "elasticsearch", "elastic search", "elk stack",
            "kibana", "logstash", "lucene",
            "inverted index", "elasticsearch queries",
            "full text search", "search engine elasticsearch",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ AI/ML (missing subtopics) ─────────────────────────────────
# =========================================================================
 
    "Statistics for Data Science": {
        "category": "Technical",
        "subcategory": "Statistics",
        "ai_context": (
            "Statistics: descriptive statistics, distributions (normal, binomial, "
            "Poisson), hypothesis testing (z-test, t-test, chi-square, ANOVA), "
            "p-value, confidence intervals, correlation, regression — "
            "as tested in placement exams."
        ),
        "aliases": [
            "statistics", "stats", "statistical analysis",
            "descriptive statistics", "inferential statistics",
            "hypothesis testing", "p value", "confidence interval",
            "normal distribution", "binomial distribution",
            "z test", "t test", "chi square", "anova",
            "correlation", "covariance", "regression statistics",
            "central limit theorem", "bayes theorem statistics",
        ],
    },
 
    "Feature Engineering and Selection": {
        "category": "Technical",
        "subcategory": "Feature Engineering",
        "ai_context": (
            "Feature Engineering: encoding (one-hot, label, ordinal), "
            "scaling (min-max, standard, robust), handling missing values, "
            "feature selection (filter, wrapper, embedded), "
            "dimensionality reduction — as tested in placement exams."
        ),
        "aliases": [
            "feature engineering", "feature selection",
            "one hot encoding", "label encoding",
            "feature scaling", "normalization", "standardization",
            "missing values", "imputation", "outlier detection",
            "dimensionality reduction feature",
            "pca feature", "lda feature",
        ],
    },
 
    "Model Evaluation Metrics": {
        "category": "Technical",
        "subcategory": "Model Evaluation",
        "ai_context": (
            "Model Evaluation: accuracy, precision, recall, F1 score, "
            "ROC-AUC, confusion matrix, MAE, MSE, RMSE, R-squared, "
            "cross-validation (k-fold, stratified), learning curves — "
            "as tested in placement exams."
        ),
        "aliases": [
            "model evaluation", "ml metrics", "evaluation metrics",
            "accuracy precision recall", "f1 score", "roc auc",
            "confusion matrix", "precision recall",
            "mae", "mse", "rmse", "r squared",
            "k fold cross validation", "learning curve ml",
            "overfitting underfitting metrics",
        ],
    },
 
    "Recommendation Systems": {
        "category": "Technical",
        "subcategory": "Recommendation Systems",
        "ai_context": (
            "Recommendation Systems: collaborative filtering (user-based, item-based), "
            "content-based filtering, matrix factorization (SVD), "
            "hybrid systems — as tested in placement exams."
        ),
        "aliases": [
            "recommendation system", "recommender system",
            "collaborative filtering", "content based filtering",
            "matrix factorization", "svd recommendation",
            "hybrid recommendation", "user based filtering",
            "item based filtering",
        ],
    },
 
    "Time Series Analysis": {
        "category": "Technical",
        "subcategory": "Time Series",
        "ai_context": (
            "Time Series: stationarity, ARIMA, SARIMA, exponential smoothing, "
            "trend, seasonality, autocorrelation, ADF test, "
            "LSTM for time series — as tested in placement exams."
        ),
        "aliases": [
            "time series", "time series analysis",
            "arima", "sarima", "arma",
            "stationarity", "adf test", "autocorrelation",
            "exponential smoothing", "seasonal decomposition",
            "forecasting", "time series forecasting",
        ],
    },
 
    "MLOps": {
        "category": "Technical",
        "subcategory": "MLOps",
        "ai_context": (
            "MLOps: model versioning (MLflow), experiment tracking, "
            "model deployment (Flask/FastAPI, TorchServe), model monitoring, "
            "data drift, feature stores — as tested in placement exams."
        ),
        "aliases": [
            "mlops", "ml ops", "model deployment",
            "mlflow", "kubeflow", "model monitoring",
            "data drift", "model drift", "feature store",
            "experiment tracking", "model registry",
            "torchserve", "bentoml",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ ECE (missing subtopics) ───────────────────────────────────
# =========================================================================
 
    "Operational Amplifiers": {
        "category": "Technical",
        "subcategory": "Op-Amp",
        "ai_context": (
            "Op-Amp circuits: inverting/non-inverting amplifier, voltage follower, "
            "summing amplifier, difference amplifier, integrator, differentiator, "
            "comparator, instrumentation amplifier, virtual ground concept — "
            "as tested in placement exams."
        ),
        "aliases": [
            "operational amplifier", "op amp circuits",
            "inverting amplifier", "non inverting amplifier",
            "voltage follower", "summing amplifier",
            "difference amplifier", "integrator op amp",
            "differentiator op amp", "comparator circuit",
            "instrumentation amplifier", "virtual ground",
        ],
    },
 
    "Power Amplifiers": {
        "category": "Technical",
        "subcategory": "Power Amplifiers",
        "ai_context": (
            "Power Amplifiers: Class A, B, AB, C, D, E; efficiency, "
            "push-pull, complementary symmetry, heat dissipation — "
            "as tested in placement exams."
        ),
        "aliases": [
            "power amplifiers", "class a amplifier", "class b amplifier",
            "class ab amplifier", "class c amplifier", "class d amplifier",
            "push pull amplifier", "power efficiency amplifier",
            "complementary symmetry",
        ],
    },
 
    "Oscillators": {
        "category": "Technical",
        "subcategory": "Oscillators",
        "ai_context": (
            "Oscillators: RC phase shift, Wien bridge, Colpitts, Hartley, "
            "crystal oscillators, Barkhausen criterion, LC tank circuit — "
            "as tested in placement exams."
        ),
        "aliases": [
            "oscillators", "oscillator circuits",
            "rc phase shift oscillator", "wien bridge oscillator",
            "colpitts oscillator", "hartley oscillator",
            "crystal oscillator", "barkhausen criterion",
            "lc oscillator", "quartz oscillator",
        ],
    },
 
    "Filters in Electronics": {
        "category": "Technical",
        "subcategory": "Filters",
        "ai_context": (
            "Electronic Filters: passive/active filters, Butterworth, Chebyshev, "
            "low-pass, high-pass, band-pass, band-stop, notch filter, "
            "Sallen-Key topology — as tested in placement exams."
        ),
        "aliases": [
            "filters electronics", "active filters", "passive filters",
            "butterworth filter", "chebyshev filter",
            "low pass filter design", "high pass filter design",
            "band pass filter design", "notch filter", "band stop filter",
            "sallen key",
        ],
    },
 
    "PCB Design": {
        "category": "Technical",
        "subcategory": "PCB Design",
        "ai_context": (
            "PCB Design: schematic capture, PCB layout, routing, design rules, "
            "signal integrity, EMI/EMC, Gerber files, EDA tools (KiCad, Altium, Eagle) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "pcb design", "printed circuit board",
            "pcb layout", "pcb routing", "schematic design",
            "signal integrity pcb", "emi emc",
            "kicad", "altium", "eagle eda",
            "gerber files", "pcb trace",
        ],
    },
 
    "ARM Cortex Architecture": {
        "category": "Technical",
        "subcategory": "ARM Architecture",
        "ai_context": (
            "ARM Cortex: Cortex-M series (M0/M3/M4/M7), registers, "
            "instruction set (Thumb, Thumb-2), NVIC, DMA, HAL — "
            "as tested in placement exams."
        ),
        "aliases": [
            "arm cortex", "cortex m", "cortex m3", "cortex m4",
            "arm instruction set", "thumb instruction",
            "nvic", "dma controller", "hal library",
            "stm32 programming", "arm registers",
        ],
    },
 
    "Communication Protocols": {
        "category": "Technical",
        "subcategory": "Communication Protocols",
        "ai_context": (
            "Communication Protocols: I2C (addressing, ACK/NACK), "
            "SPI (modes, MOSI/MISO/SCK/CS), UART (baud rate, parity), "
            "CAN bus, RS-232, RS-485, USB protocol — as tested in placement exams."
        ),
        "aliases": [
            "communication protocols", "i2c protocol", "spi protocol",
            "uart protocol", "can bus", "rs232", "rs485",
            "usb protocol", "i2c addressing", "spi modes",
            "serial communication protocols", "modbus",
        ],
    },
 
    "Sensor and Actuator Interfacing": {
        "category": "Technical",
        "subcategory": "Sensors",
        "ai_context": (
            "Sensors: temperature (LM35, DHT11, thermocouple), pressure, "
            "ultrasonic, IR, PIR, accelerometer, gyroscope, encoder; "
            "Actuators: DC motor, stepper motor, servo, relay — "
            "as tested in placement exams."
        ),
        "aliases": [
            "sensors", "sensor interfacing", "actuators",
            "temperature sensor", "lm35", "dht11", "ds18b20",
            "ultrasonic sensor", "hc sr04", "ir sensor",
            "pir sensor", "accelerometer", "gyroscope",
            "dc motor control", "stepper motor", "servo motor",
            "relay interfacing",
        ],
    },
 
    "Digital Communication": {
        "category": "Technical",
        "subcategory": "Digital Communication",
        "ai_context": (
            "Digital Communication: PCM, DPCM, delta modulation, "
            "line coding (NRZ, RZ, Manchester), scrambling, "
            "error correction codes (Hamming, BCH, Reed-Solomon), "
            "spread spectrum — as tested in placement exams."
        ),
        "aliases": [
            "digital communication", "pcm", "pulse code modulation",
            "delta modulation", "dpcm",
            "line coding", "nrz", "manchester encoding",
            "scrambling", "hamming code digital",
            "bch code", "reed solomon",
            "spread spectrum", "fhss", "dsss",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ EEE (missing subtopics) ───────────────────────────────────
# =========================================================================
 
    "Electrical Measurements": {
        "category": "Technical",
        "subcategory": "Measurements",
        "ai_context": (
            "Electrical Measurements: ammeters, voltmeters, wattmeters, "
            "energy meters, oscilloscopes, bridges (Wheatstone, Maxwell), "
            "PMMC instruments, CT/PT — as tested in placement exams."
        ),
        "aliases": [
            "electrical measurements", "measurements instruments",
            "ammeter", "voltmeter", "wattmeter", "energy meter",
            "oscilloscope", "wheatstone bridge", "maxwell bridge",
            "pmmc", "current transformer", "ct pt",
            "multimeter", "measurement errors",
        ],
    },
 
    "High Voltage Engineering": {
        "category": "Technical",
        "subcategory": "High Voltage Engineering",
        "ai_context": (
            "High Voltage Engineering: insulation, dielectric strength, "
            "corona discharge, lightning arrestors, surge protection, "
            "cable insulation, HV testing — as tested in placement exams."
        ),
        "aliases": [
            "high voltage engineering", "hv engineering",
            "insulation breakdown", "dielectric strength",
            "corona discharge", "lightning arrester", "surge arrester",
            "hv testing", "partial discharge",
        ],
    },
 
    "Electric Drives": {
        "category": "Technical",
        "subcategory": "Electric Drives",
        "ai_context": (
            "Electric Drives: DC drives, AC drives (VFD), speed control, "
            "torque-speed characteristics, four-quadrant operation, "
            "soft starters — as tested in placement exams."
        ),
        "aliases": [
            "electric drives", "electrical drives", "vfd",
            "variable frequency drive", "dc drive", "ac drive",
            "speed control motor", "torque speed characteristics",
            "soft starter", "motor drive",
        ],
    },
 
    "Renewable Energy Systems": {
        "category": "Technical",
        "subcategory": "Renewable Energy",
        "ai_context": (
            "Renewable Energy: solar PV (I-V curve, MPPT), wind turbines, "
            "hydroelectric, energy storage (batteries, supercapacitors), "
            "grid integration — as tested in placement exams."
        ),
        "aliases": [
            "renewable energy", "solar energy", "solar pv",
            "wind energy", "wind turbine", "mppt",
            "energy storage", "battery storage", "supercapacitor",
            "grid integration renewable", "smart grid",
            "hydroelectric", "biomass energy", "geothermal",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ MECH (missing subtopics) ──────────────────────────────────
# =========================================================================
 
    "Refrigeration and Air Conditioning": {
        "category": "Technical",
        "subcategory": "RAC",
        "ai_context": (
            "Refrigeration: VCR cycle, COP, refrigerants, compressors, "
            "condensers, evaporators; Air conditioning: psychrometry, "
            "load estimation, AHU — as tested in placement exams."
        ),
        "aliases": [
            "refrigeration", "air conditioning", "rac",
            "vcr cycle", "cop refrigeration",
            "refrigerants", "compressor refrigeration",
            "psychrometry", "psychrometric chart",
            "air conditioning load", "hvac", "ahu",
            "refrigeration and air conditioning",
        ],
    },
 
    "Turbomachinery": {
        "category": "Technical",
        "subcategory": "Turbomachinery",
        "ai_context": (
            "Turbomachinery: centrifugal pumps, reciprocating pumps, "
            "turbines (impulse/reaction), compressors, velocity triangles, "
            "specific speed — as tested in placement exams."
        ),
        "aliases": [
            "turbomachinery", "centrifugal pump", "reciprocating pump",
            "pump characteristics", "turbine types",
            "impulse turbine", "reaction turbine",
            "centrifugal compressor", "velocity triangles",
            "specific speed pump",
        ],
    },
 
    "Engineering Materials": {
        "category": "Technical",
        "subcategory": "Engineering Materials",
        "ai_context": (
            "Engineering Materials: stress-strain, crystal structure, "
            "phase diagrams (iron-carbon), heat treatment (annealing, quenching), "
            "ferrous/non-ferrous metals, polymers, composites, ceramics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "engineering materials", "material science", "materials science",
            "crystal structure", "phase diagram", "iron carbon diagram",
            "heat treatment", "annealing", "quenching", "tempering",
            "steel", "cast iron", "aluminum alloy",
            "composites", "ceramics materials", "polymers materials",
            "fatigue", "creep material", "fracture mechanics",
        ],
    },
 
    "Non-Destructive Testing": {
        "category": "Technical",
        "subcategory": "NDT",
        "ai_context": (
            "NDT: visual inspection, ultrasonic testing (UT), "
            "magnetic particle inspection (MPI), liquid penetrant testing, "
            "radiographic testing (RT), eddy current testing — "
            "as tested in placement exams."
        ),
        "aliases": [
            "ndt", "non destructive testing", "nondestructive testing",
            "ultrasonic testing", "magnetic particle inspection",
            "liquid penetrant", "radiographic testing",
            "eddy current testing", "visual inspection ndt",
        ],
    },
 
    "Robotics and Automation": {
        "category": "Technical",
        "subcategory": "Robotics",
        "ai_context": (
            "Robotics: kinematics (forward/inverse), Denavit-Hartenberg, "
            "robot programming, PLC, SCADA, industrial automation — "
            "as tested in placement exams."
        ),
        "aliases": [
            "robotics", "industrial robotics", "robot kinematics",
            "forward kinematics", "inverse kinematics",
            "denavit hartenberg", "plc programming",
            "scada", "industrial automation", "robot arm",
            "automation engineering",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ CIVIL (missing subtopics) ─────────────────────────────────
# =========================================================================
 
    "Hydraulics and Hydraulic Machines": {
        "category": "Technical",
        "subcategory": "Hydraulics",
        "ai_context": (
            "Hydraulics: open channel flow, manning's equation, Froude number, "
            "hydraulic jump, flow measurement (notches, weirs), "
            "pumps and turbines in civil context — as tested in placement exams."
        ),
        "aliases": [
            "hydraulics", "hydraulic machines civil",
            "open channel flow", "manning equation",
            "froude number", "hydraulic jump",
            "notch weir", "flow measurement hydraulics",
            "hydraulic gradient", "specific energy",
        ],
    },
 
    "Irrigation Engineering": {
        "category": "Technical",
        "subcategory": "Irrigation Engineering",
        "ai_context": (
            "Irrigation Engineering: canal design, duty delta base period, "
            "waterlogging, drainage, drip/sprinkler irrigation, "
            "water resources — as tested in placement exams."
        ),
        "aliases": [
            "irrigation engineering", "irrigation", "canal design",
            "duty delta", "waterlogging", "drainage irrigation",
            "drip irrigation", "sprinkler irrigation",
            "water resources engineering",
        ],
    },
 
    "Hydrology": {
        "category": "Technical",
        "subcategory": "Hydrology",
        "ai_context": (
            "Hydrology: hydrological cycle, precipitation, runoff, infiltration, "
            "hydrograph, unit hydrograph, flood estimation, groundwater — "
            "as tested in placement exams."
        ),
        "aliases": [
            "hydrology", "hydrological cycle", "precipitation",
            "runoff", "infiltration", "hydrograph",
            "unit hydrograph", "flood estimation",
            "groundwater", "aquifer", "water table",
        ],
    },
 
    "Steel Structures": {
        "category": "Technical",
        "subcategory": "Steel Structures",
        "ai_context": (
            "Steel Structures: IS 800, bolted/welded connections, "
            "beams (laterally restrained/unrestrained), columns, "
            "plastic analysis — as tested in placement exams."
        ),
        "aliases": [
            "steel structures", "structural steel", "steel design",
            "is 800", "bolted connections", "welded connections",
            "steel beams", "steel columns", "plastic analysis",
            "design of steel structures",
        ],
    },
 
# =========================================================================
# ── TECHNICAL ─ Chemical Engineering (missing subtopics) ──────────────────
# =========================================================================
 
    "Heat Exchangers": {
        "category": "Technical",
        "subcategory": "Heat Exchangers",
        "ai_context": (
            "Heat Exchangers: LMTD method, NTU-effectiveness, shell-and-tube, "
            "plate heat exchanger, fouling, overall heat transfer coefficient — "
            "as tested in placement exams."
        ),
        "aliases": [
            "heat exchangers", "heat exchanger design",
            "lmtd", "ntu effectiveness", "shell and tube",
            "plate heat exchanger", "fouling factor",
            "overall heat transfer coefficient",
        ],
    },
 
    "Process Safety": {
        "category": "Technical",
        "subcategory": "Process Safety",
        "ai_context": (
            "Process Safety: HAZOP, HAZID, safety instrumented systems (SIS), "
            "relief valves, pressure vessels, fire and explosion hazards, "
            "MSDS — as tested in placement exams."
        ),
        "aliases": [
            "process safety", "hazop", "hazid",
            "safety instrumented system", "sis",
            "relief valve", "pressure vessel design",
            "fire hazard", "explosion limits",
            "msds", "material safety data sheet",
        ],
    },
 
    "Polymer Engineering": {
        "category": "Technical",
        "subcategory": "Polymer Engineering",
        "ai_context": (
            "Polymer Engineering: polymerization (addition, condensation), "
            "thermoplastics vs thermosets, rubber, polymer processing "
            "(injection molding, extrusion) — as tested in placement exams."
        ),
        "aliases": [
            "polymer engineering", "polymers", "polymerization",
            "addition polymerization", "condensation polymerization",
            "thermoplastic", "thermoset", "rubber",
            "injection molding", "extrusion polymer",
            "polymer processing",
        ],
    },
 
# =========================================================================
# ── APTITUDE (missing topics) ─────────────────────────────────────────────
# =========================================================================
 
    "Boats and Streams": {
        "category": "Aptitude",
        "subcategory": "Boats & Streams",
        "ai_context": (
            "Boats and Streams aptitude: speed of boat in still water, "
            "speed of stream/current, upstream speed = boat speed - stream speed, "
            "downstream speed = boat speed + stream speed; "
            "time, distance, average speed problems — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "boats and streams", "boat and stream", "boats streams",
            "upstream downstream", "boat problems",
            "speed of boat", "speed of stream", "current speed",
            "river problems", "stream problems",
        ],
    },
 
    "Pipes and Cisterns": {
        "category": "Aptitude",
        "subcategory": "Pipes & Cisterns",
        "ai_context": (
            "Pipes and Cisterns: filling rate, emptying rate, inlet/outlet pipes, "
            "combined work rate, time to fill/empty a tank — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "pipes and cisterns problems", "cistern problems", "pipe problems",
            "tank filling", "inlet outlet", "pipe cistern",
            "filling emptying tank",
        ],
    },
 
    "Train Problems": {
        "category": "Aptitude",
        "subcategory": "Train Problems",
        "ai_context": (
            "Train problems: train crossing a pole (length/speed), "
            "crossing a platform (length of train + platform), "
            "two trains moving same/opposite direction — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "train problems", "train crossing", "trains crossing platform",
            "two trains", "train pole", "train bridge",
            "train speed distance", "trains opposite direction",
        ],
    },
 
    "Number Series": {
        "category": "Aptitude",
        "subcategory": "Number Series",
        "ai_context": (
            "Number series: arithmetic progression, geometric progression, "
            "Fibonacci, prime series, square/cube series, "
            "missing number, wrong number in series — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "number series", "series problems", "arithmetic series",
            "geometric series", "fibonacci series",
            "missing number series", "wrong number series",
            "pattern series", "sequence problems",
        ],
    },
 
    "Clocks": {
        "category": "Aptitude",
        "subcategory": "Clocks",
        "ai_context": (
            "Clock problems: angle between hands, coincidence of hands, "
            "minute/hour hand speed, time gained/lost by clock — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "clock problems", "clock", "clock angles",
            "hands of clock", "minute hand hour hand",
            "angle between hands", "clock coincidence",
            "fast slow clock",
        ],
    },
 
    "Calendar": {
        "category": "Aptitude",
        "subcategory": "Calendar",
        "ai_context": (
            "Calendar problems: day of week, odd days, leap year, "
            "Zeller's formula, century calendar — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "calendar problems", "calendar", "day of week",
            "odd days", "leap year calendar",
            "day calculation", "zeller formula",
        ],
    },
 
    "Races and Games": {
        "category": "Aptitude",
        "subcategory": "Races & Games",
        "ai_context": (
            "Races and Games of Skill: head start, beat by, "
            "dead heat, distance/time in races — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "races", "races and games", "race problems",
            "head start", "games of skill",
            "race track problems",
        ],
    },
 
    "Stocks and Shares": {
        "category": "Aptitude",
        "subcategory": "Stocks & Shares",
        "ai_context": (
            "Stocks and Shares: face value, market value, dividend, yield, "
            "brokerage, debentures — as tested in placement aptitude exams."
        ),
        "aliases": [
            "stocks and shares", "stocks", "shares",
            "dividend", "yield stocks", "face value",
            "market value", "brokerage", "debentures",
        ],
    },
 
    "True Discount and Banker's Discount": {
        "category": "Aptitude",
        "subcategory": "Discount",
        "ai_context": (
            "True Discount: present worth, true discount, banker's discount, "
            "banker's gain — as tested in placement aptitude exams."
        ),
        "aliases": [
            "true discount", "bankers discount", "banker's discount",
            "present worth", "banker's gain", "true discount problems",
        ],
    },
 
    "Surds and Indices": {
        "category": "Aptitude",
        "subcategory": "Surds & Indices",
        "ai_context": (
            "Surds and Indices: laws of exponents, simplification of surds, "
            "rationalization, negative/fractional exponents — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "surds and indices", "surds", "indices",
            "laws of exponents", "exponents", "powers",
            "rationalization", "surd simplification",
        ],
    },
 
    "Area and Volume": {
        "category": "Aptitude",
        "subcategory": "Area & Volume",
        "ai_context": (
            "Area and Volume: rectangle, square, triangle, circle, trapezium; "
            "cube, cuboid, cylinder, cone, sphere, hemisphere — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "area and volume", "area problems", "volume problems",
            "area of circle", "area of triangle", "area of rectangle",
            "area of trapezium", "area of rhombus",
            "volume of cylinder", "volume of cone", "volume of sphere",
            "surface area problems", "area perimeter problems",
        ],
    },
 
    "Chain Rule": {
        "category": "Aptitude",
        "subcategory": "Chain Rule",
        "ai_context": (
            "Chain Rule: direct and inverse proportion chains, "
            "multi-variable proportion problems — "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "chain rule aptitude", "chain rule", "unitary method",
            "proportion chain", "direct proportion",
            "inverse proportion chain",
        ],
    },
 
# =========================================================================
# ── VERBAL (missing topics) ────────────────────────────────────────────────
# =========================================================================
 
    "Cloze Test": {
        "category": "Verbal",
        "subcategory": "Cloze Test",
        "ai_context": (
            "Cloze Test: fill multiple blanks in a passage to test "
            "vocabulary, grammar, reading comprehension together — "
            "as tested in placement verbal exams."
        ),
        "aliases": [
            "cloze test", "cloze passage", "cloze",
            "passage blanks", "fill blanks passage",
        ],
    },
 
    "Spotting Errors": {
        "category": "Verbal",
        "subcategory": "Error Spotting",
        "ai_context": (
            "Spotting Errors: identify grammatical errors in sentences "
            "(subject-verb agreement, tense, article, preposition, "
            "pronoun usage) — as tested in placement verbal exams."
        ),
        "aliases": [
            "spotting errors", "spot the error", "error spotting",
            "find the error", "grammatical error",
            "error in sentence", "identify error",
        ],
    },
 
    "Word Arrangement": {
        "category": "Verbal",
        "subcategory": "Word Arrangement",
        "ai_context": (
            "Word Arrangement: rearrange words to form meaningful sentences, "
            "find the correct sentence structure — "
            "as tested in placement verbal exams."
        ),
        "aliases": [
            "word arrangement", "sentence arrangement",
            "rearrange words", "word order",
            "correct sentence", "jumbled words",
        ],
    },
 
    "Active and Passive Voice": {
        "category": "Verbal",
        "subcategory": "Voice",
        "ai_context": (
            "Active and Passive Voice: conversion across all tenses, "
            "when to use passive, imperative sentences, interrogative sentences — "
            "as tested in placement verbal exams."
        ),
        "aliases": [
            "active passive voice", "voice conversion",
            "active voice", "passive voice",
            "active to passive", "passive to active",
            "voice grammar",
        ],
    },
 
    "Direct and Indirect Speech": {
        "category": "Verbal",
        "subcategory": "Narration",
        "ai_context": (
            "Reported Speech: reporting verbs, pronoun changes, "
            "tense backshift, time expression changes, "
            "direct to indirect and vice versa — as tested in placement verbal exams."
        ),
        "aliases": [
            "direct indirect speech", "reported speech",
            "narration", "direct to indirect", "indirect to direct",
            "reported speech rules", "speech conversion",
        ],
    },
 
    "Reading Skills": {
        "category": "Verbal",
        "subcategory": "Reading Skills",
        "ai_context": (
            "Reading Skills: skimming, scanning, inference questions, "
            "author's tone (critical/appreciative/neutral), "
            "title/theme of passage — as tested in placement verbal exams."
        ),
        "aliases": [
            "reading skills", "reading strategy",
            "skimming scanning", "inference", "author tone",
            "theme of passage", "passage title",
        ],
    },
 
    "Verbal Analogies": {
        "category": "Verbal",
        "subcategory": "Analogies",
        "ai_context": (
            "Verbal Analogies: word pair relationships (part-whole, cause-effect, "
            "tool-function, synonym-antonym analogies) — "
            "as tested in placement verbal exams."
        ),
        "aliases": [
            "verbal analogies", "word analogies", "analogy verbal",
            "relationship analogy", "word pair",
            "analogies english", "analogy problems",
        ],
    },
 
# =========================================================================
# ── EMERGING / INTERDISCIPLINARY (missing) ────────────────────────────────
# =========================================================================
 
    "Internet of Things": {
        "category": "Technical",
        "subcategory": "IoT",
        "ai_context": (
            "IoT: IoT architecture, MQTT protocol, edge computing, "
            "fog computing, sensors & actuators, cloud IoT platforms "
            "(AWS IoT, Azure IoT Hub), security in IoT — "
            "as tested in placement exams."
        ),
        "aliases": [
            "iot", "internet of things", "iot architecture",
            "mqtt", "iot protocols", "edge computing",
            "fog computing", "aws iot", "azure iot",
            "iot security", "smart devices",
            "connected devices", "iot sensors",
        ],
    },
 
    "Data Warehousing and Mining": {
        "category": "Technical",
        "subcategory": "Data Warehousing",
        "ai_context": (
            "Data Warehousing: OLAP vs OLTP, star schema, snowflake schema, "
            "ETL process, data marts; Data Mining: association rules, "
            "Apriori, classification, clustering — as tested in placement exams."
        ),
        "aliases": [
            "data warehousing", "data warehouse", "data mining",
            "olap", "oltp", "star schema", "snowflake schema",
            "etl pipeline", "data mart",
            "association rules", "apriori algorithm",
            "data mining algorithms",
        ],
    },
 
    "Mobile App Development": {
        "category": "Technical",
        "subcategory": "Mobile Development",
        "ai_context": (
            "Mobile Development: Android (Activities, Intents, Fragments, "
            "RecyclerView, MVVM), iOS (Swift, UIKit, SwiftUI), "
            "React Native, Flutter — as tested in placement exams."
        ),
        "aliases": [
            "android development", "android", "android app",
            "ios development", "ios app",
            "react native", "flutter", "flutter dart",
            "mobile development", "mobile app development",
            "kotlin android", "swift ios", "xamarin",
            "activity android", "intent android",
        ],
    },
 
    "Cyber Law and Ethics": {
        "category": "Technical",
        "subcategory": "Cyber Law",
        "ai_context": (
            "Cyber Law: IT Act 2000, cyber crimes, digital signatures, "
            "intellectual property (copyright, patent, trademark), "
            "GDPR, data privacy — as tested in placement exams."
        ),
        "aliases": [
            "cyber law", "it act", "it act 2000", "cyber crime",
            "digital signature", "intellectual property",
            "copyright", "patent", "trademark",
            "gdpr", "data privacy", "information security law",
        ],
    },
 
    "Cloud Security": {
        "category": "Technical",
        "subcategory": "Cloud Security",
        "ai_context": (
            "Cloud Security: shared responsibility model, IAM, "
            "encryption at rest/transit, VPC security groups, NACL, "
            "WAF, DDoS protection, compliance (SOC2, ISO 27001) — "
            "as tested in placement exams."
        ),
        "aliases": [
            "cloud security", "aws security", "azure security",
            "iam aws security", "shared responsibility",
            "vpc security", "security groups", "nacl",
            "waf cloud", "ddos protection",
            "cloud compliance", "soc2", "iso 27001",
        ],
    },
 
    "Parallel Computing": {
        "category": "Technical",
        "subcategory": "Parallel Computing",
        "ai_context": (
            "Parallel Computing: Flynn's taxonomy (SISD/MIMD/SIMD/MISD), "
            "Amdahl's law, MPI, OpenMP, CUDA, GPU programming basics — "
            "as tested in placement exams."
        ),
        "aliases": [
            "parallel computing", "parallel programming",
            "flynn taxonomy", "simd", "mimd",
            "amdahl law", "mpi", "openmp",
            "cuda", "gpu programming", "parallel algorithms",
            "distributed computing",
        ],
    },
 
    "Distributed Systems": {
        "category": "Technical",
        "subcategory": "Distributed Systems",
        "ai_context": (
            "Distributed Systems: consistency models, consensus algorithms "
            "(Paxos, Raft), distributed transactions, two-phase commit, "
            "eventual consistency, Lamport clocks — as tested in placement exams."
        ),
        "aliases": [
            "distributed systems", "distributed computing",
            "paxos", "raft consensus", "consensus algorithm",
            "distributed transactions", "two phase commit",
            "eventual consistency", "lamport clock",
            "vector clock", "distributed database",
            "zookeeper", "etcd",
        ],
    },
 
    "Information Retrieval": {
        "category": "Technical",
        "subcategory": "Information Retrieval",
        "ai_context": (
            "Information Retrieval: indexing, TF-IDF, BM25, "
            "precision/recall in IR, vector space model, "
            "web crawling — as tested in placement exams."
        ),
        "aliases": [
            "information retrieval", "ir", "tf idf", "bm25",
            "inverted index ir", "web crawling",
            "search engine basics", "vector space model ir",
            "precision recall ir",
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
            "upstream", "downstream", "speed of stream",
            "average speed", "races",
            "time distance", "speed distance",
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
    "c", "r",
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
# SECTION 5 - FUZZY SCORE HELPER  (NEW in v6.0)
# ===========================================================================

def _fuzzy_score(a: str, b: str) -> float:
    """
    Bigram-based Dice coefficient similarity.
    Returns 0.0 – 1.0.  Fast enough to scan the full alias index.
    """
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
    """
    Scan entire alias index and return (best_canonical, best_score).
    Only considers aliases whose length is within 60% – 200% of query length
    to avoid wildly mismatched comparisons.
    """
    q_len = len(query)
    best_canon = None
    best_score = 0.0

    for alias, canon in _ALIAS_INDEX.items():
        # Length gate — skip obviously wrong-length aliases
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

    # Unwrap multi-entry to first canonical
    if best_canon and best_canon.startswith("__MULTI__"):
        parts = [c for c in best_canon[len("__MULTI__"):].split("||") if c in CANONICAL_TOPICS]
        best_canon = parts[0] if parts else None

    return best_canon, best_score


# ===========================================================================
# SECTION 6 - CORE RESOLVER  (updated in v6.0)
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

    # ── 4. Fuzzy match — catch typos ("pyhton", "java scrop", etc.) ───────
    best_canon, best_score = _best_fuzzy_match(clean)

    # High confidence → silently auto-correct
    if best_score >= 0.75 and best_canon and best_canon in CANONICAL_TOPICS:
        return _make_result(best_canon)

    # Medium confidence → reject but suggest the closest topic
    if best_score >= 0.55 and best_canon and best_canon in CANONICAL_TOPICS:
        suggested = CANONICAL_TOPICS[best_canon]["subcategory"]
        return {
            "status": "invalid",
            "message": (
                f'"{raw}" doesn\'t match any topic. '
                f'Did you mean "{suggested}"?'
            ),
        }

    # ── 5. Reject short / single-word queries that matched nothing ────────
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

    # ── 6. Reject if all words look like gibberish (no vowels) ───────────
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

    # ── 7. Allow as NEW topic only if it contains real-looking words ──────
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

    # Passed all checks — accept as a brand-new topic
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
# SECTION 8 - SELF TEST
# ===========================================================================

if __name__ == "__main__":
    tests = [
        # Languages
        ("c",                       "C Programming"),
        ("cpp",                     "C++ Programming"),
        ("java",                    "Java Programming"),
        ("python",                  "Python Programming"),
        ("js",                      "JavaScript"),
        ("ts",                      "TypeScript"),
        ("golang",                  "Golang"),
        ("kotlin",                  "Kotlin"),
        ("rust",                    "Rust"),
        ("sql",                     "SQL"),
        ("nosql",                   "NoSQL"),
        ("mongodb",                 "NoSQL"),
        ("react",                   "React"),
        ("reactjs",                 "React"),
        ("angular",                 "Angular"),
        ("vue",                     "Vue.js"),
        ("nodejs",                  "Node.js"),
        ("express",                 "Node.js"),
        ("django",                  "Django"),
        ("flask",                   "Flask"),
        ("spring boot",             "Spring Boot"),
        ("rest api",                "REST APIs"),
        ("jwt",                     "REST APIs"),
        ("docker",                  "Docker"),
        ("kubernetes",              "Kubernetes"),
        ("k8s",                     "Kubernetes"),
        ("aws",                     "AWS"),
        ("ec2",                     "AWS"),
        ("devops",                  "DevOps"),
        ("jenkins",                 "DevOps"),
        ("terraform",               "DevOps"),
        # DSA
        ("dsa",                     "Data Structures"),
        ("linked list",             "Linked Lists"),
        ("bst",                     "Trees"),
        ("heap",                    "Heaps"),
        ("bfs",                     "Graphs"),
        ("dijkstra",                "Graphs"),
        ("dp",                      "Dynamic Programming"),
        ("greedy",                  "Greedy Algorithms"),
        ("sorting",                 "Sorting Algorithms"),
        ("binary search",           "Searching Algorithms"),
        ("bit manipulation",        "Bit Manipulation"),
        ("sliding window",          "Sliding Window"),
        ("two pointer",             "Sliding Window"),
        ("trie",                    "Tries"),
        # DBMS
        ("dbms",                    "DBMS"),
        ("bcnf",                    "Normalization"),
        ("acid",                    "ACID and Transactions"),
        ("inner join",              "Database Joins"),
        # OS
        ("os",                      "Operating Systems"),
        ("deadlock",                "Deadlock"),
        ("round robin",             "CPU Scheduling"),
        ("semaphore",               "Process Synchronization"),
        ("lru",                     "Memory Management"),
        # CN
        ("osi",                     "OSI Model"),
        ("tcp",                     "TCP/IP and Protocols"),
        ("subnetting",              "IP Addressing and Subnetting"),
        ("dns",                     "Application Layer Protocols"),
        # CS theory
        ("compiler design",         "Compiler Design"),
        ("lex",                     "Compiler Design"),
        ("automata",                "Theory of Computation"),
        ("turing machine",          "Theory of Computation"),
        ("computer architecture",   "Computer Architecture"),
        ("pipelining",              "Computer Architecture"),
        ("discrete math",           "Discrete Mathematics"),
        # ML/AI
        ("machine learning",        "Machine Learning"),
        ("deep learning",           "Deep Learning"),
        ("cnn",                     "Deep Learning"),
        ("nlp",                     "Natural Language Processing"),
        ("bert",                    "Natural Language Processing"),
        ("data science",            "Data Science"),
        ("pandas",                  "Data Science"),
        ("hadoop",                  "Big Data"),
        ("spark",                   "Big Data"),
        # ECE
        ("vlsi",                    "VLSI Design"),
        ("verilog",                 "VLSI Design"),
        ("op amp",                  "Analog Electronics"),
        ("flip flop",               "Digital Electronics"),
        ("pid",                     "Control Systems"),
        ("fourier",                 "Signal Processing"),
        ("8085",                    "Microprocessors"),
        ("arduino",                 "Embedded Systems"),
        ("iot",                     "Embedded Systems"),
        # EEE
        ("thevenin",                "Circuit Theory"),
        ("transformer",             "Electrical Machines"),
        ("thyristor",               "Power Electronics"),
        # MECH
        ("carnot cycle",            "Thermodynamics"),
        ("bernoulli",               "Fluid Mechanics"),
        ("som",                     "Strength of Materials"),
        ("cnc",                     "Manufacturing Technology"),
        ("spur gear",               "Machine Design"),
        # CIVIL
        ("rcc",                     "Concrete Technology"),
        ("pile foundation",         "Geotechnical Engineering"),
        ("surveying",               "Surveying"),
        ("structural analysis",     "Structural Analysis"),
        # Aptitude
        ("hcf",                     "Number System"),
        ("percentage",              "Percentages"),
        ("profit",                  "Profit and Loss"),
        ("si ci",                   "Simple and Compound Interest"),
        ("pipes",                   "Time and Work"),
        ("trains",                  "Time Speed Distance"),
        ("boats",                   "Time Speed Distance"),
        ("upstream",                "Time Speed Distance"),
        ("speed",                   "Time Speed Distance"),
        ("syllogism",               "Logical Reasoning"),
        ("blood relation",          "Logical Reasoning"),
        ("di",                      "Data Interpretation"),
        ("mensuration",             "Mensuration"),
        ("trigonometry",            "Trigonometry"),
        ("algebra",                 "Algebra"),
        # Verbal
        ("grammar",                 "Grammar"),
        ("synonyms",                "Vocabulary"),
        ("comprehension",           "Reading Comprehension"),
        ("error detection",         "Sentence Correction"),
        ("para jumble",             "Para Jumbles"),
        # Blockchain/emerging
        ("blockchain",              "Blockchain"),
        ("solidity",                "Blockchain"),
        # Typo correction (NEW in v6.0)
        ("pyhton",                  "Python Programming"),
        ("javascrip",               "JavaScript"),
        ("dynmic programming",      "Dynamic Programming"),
        ("machne learning",         "Machine Learning"),
        ("databse",                 "DBMS"),
        # Should be INVALID (gibberish / noise)
        ("java scrop",              "INVALID"),
        ("hello",                   "INVALID"),
        ("aaaa",                    "INVALID"),
        ("1234",                    "INVALID"),
        ("xyz",                     "INVALID"),
        ("qwerty",                  "INVALID"),
        ("water",                   "INVALID"),
        ("food",                    "INVALID"),
        ("red",                     "INVALID"),
        ("jjj",                     "INVALID"),
        ("kkk",                     "INVALID"),
        ("scrop",                   "INVALID"),
        ("blarg",                   "INVALID"),
        ("xyzabc",                  "INVALID"),
        # Should be NEW topic
        ("metaverse development",   "NEW"),
        ("competitive programming", "NEW"),
        ("robotics programming",    "NEW"),
    ]

    pass_count = fail_count = 0
    print(f"\n{'═' * 105}")
    print(f"{'QUERY':<32} {'EXPECTED':<30} {'GOT':<38} RESULT")
    print(f"{'═' * 105}")

    for query, expected in tests:
        r = resolve_topic(query)
        st = r["status"]

        if st == "single":
            got_label = r["canonical"]
        elif st == "multi":
            got_label = "MULTI: " + " | ".join(o["canonical"] for o in r["options"][:3])
        elif st == "new":
            got_label = "NEW"
        else:
            got_label = f"INVALID: {r.get('message', '')[:40]}"

        if expected == "INVALID":
            ok = (st == "invalid")
        elif expected == "NEW":
            ok = (st == "new")
        else:
            ok = (st == "single" and r.get("canonical") == expected) or \
                 (st == "multi" and any(o["canonical"] == expected for o in r.get("options", [])))

        mark = "✅" if ok else "❌"
        if ok:
            pass_count += 1
        else:
            fail_count += 1
        print(f"{query:<32} {expected:<30} {got_label:<38} {mark}")

    print(f"{'═' * 105}")
    print(f"Results: {pass_count} passed, {fail_count} failed / {len(tests)} total")
    print(f"{'═' * 105}\n")