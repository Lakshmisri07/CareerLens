"""
smart_topic_resolver.py  –  v3.0
==================================
Architecture
------------
1. CANONICAL_TOPICS  – the single source of truth.
   Every placement-relevant topic lives here exactly once, with:
     - canonical_name   : the display name used everywhere
     - category         : Technical | Aptitude | Verbal
     - subcategory      : finer grouping (used for subtopic routing)
     - ai_context       : what the AI should generate questions about
     - aliases          : every spelling / abbreviation / partial name
                          that should resolve to this topic

2. resolve_topic(query) – looks up the query against all aliases,
   returns a structured dict consumed by the Flask endpoint.

3. _is_valid_query(query) – rejects pure garbage (random letters,
   digits, noise words) before hitting the alias lookup.

Key design decisions
--------------------
- One canonical name per topic, many aliases.  No ambiguity.
- Aliases are all lowercase; matching is case-insensitive.
- A query that is a PREFIX of an alias also matches (min 4 chars),
  so "sort" -> "sorting algorithms", "boat" -> "boats and streams".
- If a query matches aliases from MORE than one canonical topic
  the resolver returns 'multi' so the user can pick.
- If a query passes the validity check but matches nothing, it is
  returned as 'new' so the dashboard can add it dynamically.
- Garbage / noise returns 'invalid' with a helpful hint message.
"""

import re
from typing import Dict, List

# ===========================================================================
# SECTION 1 - CANONICAL TOPIC REGISTRY
# ===========================================================================
# Structure of each entry:
#   "Canonical Name": {
#       "category": "Technical" | "Aptitude" | "Verbal",
#       "subcategory": str,          # used as subtopic in quiz URL
#       "ai_context": str,           # injected into AI prompt
#       "aliases": [str, ...]        # all lowercase alternative names
#   }
# ===========================================================================

CANONICAL_TOPICS: Dict[str, dict] = {

    # -------------------------------------------------------------------------
    # TECHNICAL - Programming Languages
    # -------------------------------------------------------------------------

    "C Programming": {
        "category": "Technical",
        "subcategory": "C",
        "ai_context": (
            "C programming language: data types, operators, control flow, "
            "arrays, strings, pointers, pointer arithmetic, functions, "
            "recursion, structures, unions, file I/O, memory management, "
            "malloc/free, preprocessor directives - as tested in placement exams."
        ),
        "aliases": [
            "c", "c programming", "c language", "c lang", "c prog",
            "c basics", "c fundamentals", "programming in c",
            "c pointers", "c arrays", "c functions", "c loops",
            "c strings", "c structures", "c unions", "c file handling",
        ],
    },

    "C++ Programming": {
        "category": "Technical",
        "subcategory": "C++",
        "ai_context": (
            "C++ programming: classes and objects, constructors/destructors, "
            "inheritance, polymorphism, operator overloading, templates, STL "
            "(vector, map, set, stack, queue), exception handling, smart pointers, "
            "virtual functions, abstract classes - as tested in placement exams."
        ),
        "aliases": [
            "c++", "cpp", "c plus plus", "cplusplus", "c++ programming",
            "c++ language", "stl", "standard template library",
            "c++ stl", "c++ oops", "c++ oop",
            "vector", "c++ vector", "c++ map", "c++ set",
            "operator overloading", "templates", "smart pointers",
            "virtual functions",
        ],
    },

    "Java Programming": {
        "category": "Technical",
        "subcategory": "Java",
        "ai_context": (
            "Java programming: OOP concepts, classes and objects, inheritance, "
            "polymorphism, abstraction, encapsulation, interfaces, abstract classes, "
            "exception handling, collections framework (ArrayList, HashMap, LinkedList), "
            "multithreading, Java 8 features (streams, lambdas), JDBC basics - "
            "as tested in placement exams."
        ),
        "aliases": [
            "java", "java programming", "java language", "core java",
            "java basics", "java fundamentals", "java oops", "java oop",
            "java collections", "java multithreading", "java 8",
            "java streams", "java lambda", "java generics",
            "arraylist", "hashmap", "linked list java",
            "java exception", "java interface",
        ],
    },

    "Python Programming": {
        "category": "Technical",
        "subcategory": "Python",
        "ai_context": (
            "Python programming: data types, lists, tuples, sets, dictionaries, "
            "comprehensions, functions, lambda, decorators, generators, iterators, "
            "OOP in Python, file handling, exception handling, modules, "
            "NumPy and Pandas basics - as tested in placement exams."
        ),
        "aliases": [
            "python", "python programming", "python language", "python basics",
            "python fundamentals", "python oops", "python oop", "python3",
            "python lists", "python dict", "python dictionaries",
            "python tuples", "python sets", "python functions",
            "python decorators", "python generators", "python file handling",
            "python modules", "python packages",
        ],
    },

    "JavaScript": {
        "category": "Technical",
        "subcategory": "JavaScript",
        "ai_context": (
            "JavaScript: variables (var/let/const), data types, functions, "
            "closures, prototypes, ES6+ features (arrow functions, destructuring, "
            "spread/rest, promises, async/await), DOM manipulation, event handling, "
            "fetch API, modules - as tested in placement exams."
        ),
        "aliases": [
            "javascript", "js", "java script", "es6", "es2015",
            "ecmascript", "javascript es6", "vanilla js", "js basics",
            "node.js", "nodejs", "node js",
            "promises", "async await", "closures",
        ],
    },

    "TypeScript": {
        "category": "Technical",
        "subcategory": "TypeScript",
        "ai_context": (
            "TypeScript: static typing, interfaces, type aliases, generics, "
            "enums, decorators, modules, type narrowing, utility types - "
            "as tested in placement exams."
        ),
        "aliases": [
            "typescript", "ts", "type script",
        ],
    },

    "Golang": {
        "category": "Technical",
        "subcategory": "Golang",
        "ai_context": (
            "Go programming: goroutines, channels, interfaces, structs, "
            "error handling, slices, maps, packages, concurrency model - "
            "as tested in placement exams."
        ),
        "aliases": [
            "golang", "go lang", "go programming", "go language",
            "goroutines", "go channels", "go interfaces",
        ],
    },

    "Kotlin": {
        "category": "Technical",
        "subcategory": "Kotlin",
        "ai_context": (
            "Kotlin: null safety, data classes, extension functions, coroutines, "
            "sealed classes, smart casts, lambdas, collections - "
            "as tested in placement exams."
        ),
        "aliases": [
            "kotlin", "kotlin programming", "kotlin android",
        ],
    },

    "Ruby": {
        "category": "Technical",
        "subcategory": "Ruby",
        "ai_context": (
            "Ruby: blocks, procs, lambdas, modules, mixins, "
            "symbols, hashes, Ruby on Rails basics - "
            "as tested in placement exams."
        ),
        "aliases": [
            "ruby", "ruby programming", "ruby on rails", "rails",
        ],
    },

    "SQL": {
        "category": "Technical",
        "subcategory": "SQL",
        "ai_context": (
            "SQL queries: SELECT, INSERT, UPDATE, DELETE, WHERE, GROUP BY, "
            "HAVING, ORDER BY, DISTINCT, aggregate functions (COUNT/SUM/AVG/MAX/MIN), "
            "subqueries, correlated subqueries, CASE, COALESCE, window functions - "
            "as tested in placement exams."
        ),
        "aliases": [
            "sql", "structured query language", "sql queries", "sql basics",
            "sql commands", "sql functions", "sql aggregates",
            "mysql", "my sql", "postgresql", "postgres", "oracle sql",
            "ms sql", "sql server", "sqlite",
            "sql subquery", "sql joins query",
            "window functions", "sql window",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Data Structures
    # -------------------------------------------------------------------------

    "Data Structures": {
        "category": "Technical",
        "subcategory": "Data Structures",
        "ai_context": (
            "Data structures: arrays, linked lists (singly, doubly, circular), "
            "stacks, queues, deque, trees (binary tree, BST, AVL), heaps, "
            "hash tables, graphs, tries - operations, time/space complexity, "
            "applications - as tested in placement exams."
        ),
        "aliases": [
            "data structures", "dsa", "ds", "data structure",
            "data structures and algorithms",
        ],
    },

    "Linked Lists": {
        "category": "Technical",
        "subcategory": "Linked Lists",
        "ai_context": (
            "Linked Lists: singly linked list, doubly linked list, circular linked list; "
            "insertion (at beginning/end/position), deletion, traversal, reversal, "
            "cycle detection (Floyd's algorithm), merge two sorted lists, "
            "find middle element, nth from end - as tested in placement exams."
        ),
        "aliases": [
            "linked list", "linked lists", "singly linked list",
            "doubly linked list", "circular linked list",
            "ll", "linkedlist",
        ],
    },

    "Stacks and Queues": {
        "category": "Technical",
        "subcategory": "Stacks and Queues",
        "ai_context": (
            "Stacks: LIFO, push/pop/peek, balanced parentheses, infix to postfix, "
            "postfix evaluation, stack using queue; "
            "Queues: FIFO, enqueue/dequeue, circular queue, deque, "
            "priority queue, queue using stacks - as tested in placement exams."
        ),
        "aliases": [
            "stack", "stacks", "stack data structure",
            "queue", "queues", "circular queue", "deque",
            "priority queue", "stacks and queues",
            "infix postfix", "balanced parentheses",
        ],
    },

    "Trees": {
        "category": "Technical",
        "subcategory": "Trees",
        "ai_context": (
            "Trees: binary tree, binary search tree (BST), AVL tree, red-black tree, "
            "B-tree, B+ tree; tree traversals (inorder, preorder, postorder, "
            "level order), height, diameter, LCA, tree DP, segment tree - "
            "as tested in placement exams."
        ),
        "aliases": [
            "tree", "trees", "binary tree", "bst", "binary search tree",
            "avl tree", "avl", "red black tree", "b tree", "b+ tree",
            "segment tree", "fenwick tree", "binary indexed tree",
            "tree traversal", "inorder", "preorder", "postorder",
            "level order traversal", "tree height",
            "tree diameter", "lca", "lowest common ancestor",
        ],
    },

    "Heaps": {
        "category": "Technical",
        "subcategory": "Heaps",
        "ai_context": (
            "Heaps: min heap, max heap, heapify, insertion, deletion, "
            "heap sort, priority queue implementation using heap, "
            "k-th largest/smallest element, merge k sorted lists - "
            "as tested in placement exams."
        ),
        "aliases": [
            "heap", "heaps", "min heap", "max heap",
            "heap sort", "heapify", "priority heap",
        ],
    },

    "Hashing": {
        "category": "Technical",
        "subcategory": "Hashing",
        "ai_context": (
            "Hashing: hash functions, hash tables, collision resolution "
            "(chaining, open addressing - linear probing, quadratic probing, "
            "double hashing), load factor, rehashing, applications of hashing, "
            "string hashing - as tested in placement exams."
        ),
        "aliases": [
            "hashing", "hash table", "hash map", "hashmap",
            "hash set", "hash function",
            "collision resolution", "chaining", "open addressing",
        ],
    },

    "Graphs": {
        "category": "Technical",
        "subcategory": "Graphs",
        "ai_context": (
            "Graphs: directed/undirected graphs, weighted graphs, adjacency matrix, "
            "adjacency list, BFS, DFS, topological sort, cycle detection, "
            "connected components, strongly connected components (Kosaraju, Tarjan), "
            "shortest path (Dijkstra, Bellman-Ford, Floyd-Warshall), "
            "minimum spanning tree (Kruskal, Prim) - as tested in placement exams."
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
            "strongly connected components", "scc",
            "graph traversal",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Algorithms
    # -------------------------------------------------------------------------

    "Algorithms": {
        "category": "Technical",
        "subcategory": "Algorithms",
        "ai_context": (
            "Algorithms: sorting (bubble, selection, insertion, merge, quick, heap), "
            "searching (linear, binary), recursion, divide and conquer, "
            "time/space complexity, Big O notation - "
            "as tested in placement exams."
        ),
        "aliases": [
            "algorithms", "algorithm", "algo", "algos",
        ],
    },

    "Sorting Algorithms": {
        "category": "Technical",
        "subcategory": "Sorting",
        "ai_context": (
            "Sorting Algorithms: bubble sort, selection sort, insertion sort, "
            "merge sort, quick sort (pivot, partition), heap sort, "
            "counting sort, radix sort, bucket sort; "
            "stability, time and space complexity comparison - "
            "as tested in placement exams."
        ),
        "aliases": [
            "sorting", "sorting algorithms", "sorting techniques",
            "bubble sort", "selection sort", "insertion sort",
            "merge sort", "quick sort", "heap sort",
            "radix sort", "counting sort", "bucket sort",
            "stable sort", "unstable sort",
        ],
    },

    "Searching Algorithms": {
        "category": "Technical",
        "subcategory": "Searching",
        "ai_context": (
            "Searching Algorithms: linear search, binary search, "
            "ternary search, jump search, interpolation search, "
            "exponential search; binary search on answer, "
            "applications of binary search - as tested in placement exams."
        ),
        "aliases": [
            "searching", "searching algorithms", "linear search", "binary search",
            "ternary search", "jump search", "interpolation search",
            "binary search problems",
        ],
    },

    "Dynamic Programming": {
        "category": "Technical",
        "subcategory": "Dynamic Programming",
        "ai_context": (
            "Dynamic Programming: overlapping subproblems, optimal substructure, "
            "memoization, tabulation, classic DP problems - "
            "0/1 knapsack, unbounded knapsack, LCS, LIS, edit distance, "
            "coin change, matrix chain multiplication, DP on trees, "
            "DP on strings - as tested in placement exams."
        ),
        "aliases": [
            "dynamic programming", "dp", "dp problems",
            "memoization", "tabulation", "bottom up dp", "top down dp",
            "knapsack", "0/1 knapsack", "unbounded knapsack",
            "lcs", "longest common subsequence",
            "lis", "longest increasing subsequence",
            "edit distance", "coin change dp",
            "matrix chain multiplication",
        ],
    },

    "Greedy Algorithms": {
        "category": "Technical",
        "subcategory": "Greedy",
        "ai_context": (
            "Greedy Algorithms: greedy choice property, optimal substructure, "
            "activity selection, fractional knapsack, job scheduling, "
            "Huffman coding, minimum coin change (greedy), "
            "interval scheduling - as tested in placement exams."
        ),
        "aliases": [
            "greedy", "greedy algorithms", "greedy method", "greedy approach",
            "activity selection", "fractional knapsack",
            "huffman coding", "job scheduling greedy",
        ],
    },

    "Backtracking": {
        "category": "Technical",
        "subcategory": "Backtracking",
        "ai_context": (
            "Backtracking: N-queens problem, Sudoku solver, subset sum, "
            "generating permutations and combinations, rat in a maze, "
            "graph coloring, Hamiltonian cycle - "
            "as tested in placement exams."
        ),
        "aliases": [
            "backtracking", "backtrack",
            "n queens", "n-queens", "sudoku solver",
            "subset sum", "graph coloring", "hamiltonian cycle",
        ],
    },

    "Recursion": {
        "category": "Technical",
        "subcategory": "Recursion",
        "ai_context": (
            "Recursion: base case, recursive call, call stack, "
            "tail recursion, recursion vs iteration, "
            "classic problems (factorial, Fibonacci, Tower of Hanoi, "
            "flood fill, power function), tree recursion - "
            "as tested in placement exams."
        ),
        "aliases": [
            "recursion", "recursive", "recursive algorithms",
            "tail recursion", "tower of hanoi",
            "fibonacci recursion", "factorial recursion",
        ],
    },

    "Time and Space Complexity": {
        "category": "Technical",
        "subcategory": "Complexity Analysis",
        "ai_context": (
            "Time and Space Complexity: Big O, Big Theta, Big Omega, "
            "best/average/worst case, amortized analysis, "
            "P vs NP, common complexities (O(1), O(log n), O(n), O(n log n), "
            "O(n^2), O(2^n)) - as tested in placement exams."
        ),
        "aliases": [
            "time complexity", "space complexity", "big o", "big o notation",
            "complexity analysis", "asymptotic analysis",
            "big theta", "big omega", "amortized analysis",
            "p vs np", "np complete", "np hard",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - DBMS
    # -------------------------------------------------------------------------

    "DBMS": {
        "category": "Technical",
        "subcategory": "DBMS",
        "ai_context": (
            "Database Management Systems: ER model, relational model, keys "
            "(primary, foreign, candidate, super), SQL joins (inner, outer, left, right, "
            "self, cross), normalization (1NF/2NF/3NF/BCNF), functional dependencies, "
            "ACID properties, transactions, concurrency control, indexing (B-tree), "
            "views, triggers, stored procedures - as tested in placement exams."
        ),
        "aliases": [
            "dbms", "database", "databases", "database management",
            "database management system", "rdbms",
            "relational database",
        ],
    },

    "Database Joins": {
        "category": "Technical",
        "subcategory": "Joins",
        "ai_context": (
            "SQL Joins: INNER JOIN, LEFT OUTER JOIN, RIGHT OUTER JOIN, "
            "FULL OUTER JOIN, CROSS JOIN, SELF JOIN, NATURAL JOIN; "
            "join conditions, join on multiple columns, join with subqueries - "
            "as tested in placement exams."
        ),
        "aliases": [
            "joins", "join", "sql joins", "inner join", "outer join",
            "left join", "right join", "full outer join",
            "self join", "cross join", "natural join",
            "database joins",
        ],
    },

    "Normalization": {
        "category": "Technical",
        "subcategory": "Normalization",
        "ai_context": (
            "Database Normalization: functional dependencies, partial dependency, "
            "transitive dependency, 1NF (atomic values), 2NF (no partial dependency), "
            "3NF (no transitive dependency), BCNF, 4NF, 5NF; "
            "anomalies (insertion, deletion, update), decomposition - "
            "as tested in placement exams."
        ),
        "aliases": [
            "normalization", "database normalization",
            "1nf", "2nf", "3nf", "bcnf", "4nf",
            "first normal form", "second normal form", "third normal form",
            "functional dependency", "functional dependencies",
            "partial dependency", "transitive dependency",
        ],
    },

    "ACID and Transactions": {
        "category": "Technical",
        "subcategory": "Transactions",
        "ai_context": (
            "ACID Properties and Transactions: Atomicity, Consistency, Isolation, "
            "Durability; commit, rollback, savepoint; isolation levels "
            "(read uncommitted, read committed, repeatable read, serializable); "
            "concurrency control (2PL, timestamp ordering), deadlock in DBMS - "
            "as tested in placement exams."
        ),
        "aliases": [
            "acid", "acid properties", "transactions", "transaction",
            "commit rollback", "isolation levels", "concurrency control",
            "two phase locking", "2pl", "deadlock dbms",
        ],
    },

    "Indexing": {
        "category": "Technical",
        "subcategory": "Indexing",
        "ai_context": (
            "Database Indexing: clustered index, non-clustered index, "
            "B-tree index, B+ tree index, hash index, "
            "dense vs sparse index, multi-level indexing, "
            "query optimization using indexes - "
            "as tested in placement exams."
        ),
        "aliases": [
            "indexing", "database indexing", "b tree index", "b+ tree index",
            "clustered index", "non clustered index",
            "dense index", "sparse index",
        ],
    },

    "ER Model": {
        "category": "Technical",
        "subcategory": "ER Model",
        "ai_context": (
            "Entity-Relationship Model: entities, attributes, relationships, "
            "cardinality (1:1, 1:N, M:N), participation constraints, "
            "weak entities, extended ER (ISA hierarchy), "
            "converting ER to relational schema - "
            "as tested in placement exams."
        ),
        "aliases": [
            "er model", "entity relationship", "entity relationship model",
            "erd", "er diagram", "entity relationship diagram",
            "cardinality", "weak entity",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Operating Systems
    # -------------------------------------------------------------------------

    "Operating Systems": {
        "category": "Technical",
        "subcategory": "OS",
        "ai_context": (
            "Operating Systems: processes, threads, process states, PCB, "
            "CPU scheduling, deadlock, memory management, file systems, "
            "synchronization - as tested in placement exams."
        ),
        "aliases": [
            "os", "operating system", "operating systems",
        ],
    },

    "CPU Scheduling": {
        "category": "Technical",
        "subcategory": "CPU Scheduling",
        "ai_context": (
            "CPU Scheduling algorithms: FCFS, SJF (preemptive/non-preemptive), "
            "Round Robin (time quantum), Priority scheduling, HRRN; "
            "Gantt charts, turnaround time, waiting time, response time, "
            "throughput, CPU utilization - as tested in placement exams."
        ),
        "aliases": [
            "cpu scheduling", "scheduling", "scheduling algorithms",
            "fcfs", "first come first served",
            "sjf", "shortest job first", "srtf", "shortest remaining time",
            "round robin", "rr scheduling",
            "priority scheduling", "hrrn",
            "gantt chart", "turnaround time", "waiting time",
        ],
    },

    "Deadlock": {
        "category": "Technical",
        "subcategory": "Deadlock",
        "ai_context": (
            "Deadlock: four necessary conditions (mutual exclusion, hold and wait, "
            "no preemption, circular wait), deadlock prevention, "
            "deadlock avoidance (Banker's algorithm, safe state), "
            "deadlock detection (resource allocation graph), "
            "deadlock recovery - as tested in placement exams."
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
            "Memory Management: contiguous allocation, paging, segmentation, "
            "virtual memory, demand paging, page fault, "
            "page replacement algorithms (FIFO, LRU, Optimal, Clock), "
            "thrashing, working set model, TLB, page table - "
            "as tested in placement exams."
        ),
        "aliases": [
            "memory management", "paging", "segmentation",
            "virtual memory", "demand paging", "page fault",
            "page replacement", "lru", "fifo page", "optimal page replacement",
            "thrashing", "tlb", "translation lookaside buffer",
            "page table", "frame allocation",
        ],
    },

    "Process Synchronization": {
        "category": "Technical",
        "subcategory": "Synchronization",
        "ai_context": (
            "Process Synchronization: critical section, race condition, "
            "mutex, semaphore (binary and counting), monitors, "
            "producer-consumer problem, readers-writers problem, "
            "dining philosophers problem - as tested in placement exams."
        ),
        "aliases": [
            "synchronization", "process synchronization",
            "semaphore", "semaphores", "mutex",
            "critical section", "race condition", "monitor",
            "producer consumer", "readers writers", "dining philosophers",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Computer Networks
    # -------------------------------------------------------------------------

    "Computer Networks": {
        "category": "Technical",
        "subcategory": "Computer Networks",
        "ai_context": (
            "Computer Networks: OSI model (7 layers), TCP/IP model, "
            "IP addressing, routing, transport layer, application layer protocols - "
            "as tested in placement exams."
        ),
        "aliases": [
            "computer networks", "cn", "networking", "network",
            "computer networking",
        ],
    },

    "OSI Model": {
        "category": "Technical",
        "subcategory": "OSI Model",
        "ai_context": (
            "OSI Model: 7 layers (Physical, Data Link, Network, Transport, "
            "Session, Presentation, Application), functions of each layer, "
            "protocols at each layer, PDU names, "
            "OSI vs TCP/IP comparison - as tested in placement exams."
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
            "TCP/IP: TCP vs UDP comparison, TCP 3-way handshake, "
            "TCP connection termination (4-way), TCP flow control, "
            "congestion control, UDP use cases, "
            "IP (IPv4 vs IPv6), ICMP, ARP, RARP - "
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
            "IP Addressing and Subnetting: IPv4 address classes (A/B/C/D/E), "
            "subnet mask, CIDR notation, subnetting calculation, "
            "number of hosts per subnet, network address, broadcast address, "
            "private IP ranges, NAT, IPv6 basics - "
            "as tested in placement exams."
        ),
        "aliases": [
            "ip addressing", "ip address", "subnetting", "subnet",
            "subnet mask", "cidr", "ip classes",
            "class a", "class b", "class c",
            "private ip", "nat", "network address translation",
            "broadcast address",
        ],
    },

    "Application Layer Protocols": {
        "category": "Technical",
        "subcategory": "Application Layer",
        "ai_context": (
            "Application Layer Protocols: HTTP (methods, status codes, "
            "HTTP vs HTTPS), DNS (resolution, record types: A, MX, CNAME, TXT), "
            "SMTP, POP3, IMAP, FTP, DHCP, SNMP - "
            "as tested in placement exams."
        ),
        "aliases": [
            "http", "https", "http protocol", "http methods",
            "http status codes", "get post put delete",
            "dns", "domain name system", "dns resolution",
            "smtp", "pop3", "imap", "email protocols",
            "ftp", "dhcp", "snmp",
            "application layer protocols",
        ],
    },

    "Routing Protocols": {
        "category": "Technical",
        "subcategory": "Routing",
        "ai_context": (
            "Routing Protocols: static vs dynamic routing, "
            "distance vector routing (RIP, Bellman-Ford), "
            "link state routing (OSPF, Dijkstra), path vector (BGP), "
            "routing table, routing algorithms - "
            "as tested in placement exams."
        ),
        "aliases": [
            "routing", "routing protocols", "rip", "ospf", "bgp",
            "distance vector", "link state routing",
            "routing table", "static routing", "dynamic routing",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - OOP and Design
    # -------------------------------------------------------------------------

    "OOP Concepts": {
        "category": "Technical",
        "subcategory": "OOP",
        "ai_context": (
            "Object-Oriented Programming: classes, objects, encapsulation, "
            "inheritance (single, multiple, multilevel, hierarchical, hybrid), "
            "polymorphism (method overloading vs overriding), abstraction, "
            "interfaces, abstract classes, constructors, "
            "access modifiers (public, private, protected) - "
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
            "Software Design Patterns: Creational (Singleton, Factory, "
            "Abstract Factory, Builder, Prototype), Structural (Adapter, "
            "Bridge, Composite, Decorator, Facade), Behavioral (Observer, "
            "Strategy, Command, Iterator, Template Method); "
            "SOLID principles - as tested in placement exams."
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
            "mvc", "model view controller",
            "solid", "solid principles",
            "single responsibility principle", "open closed principle",
            "liskov substitution", "dependency inversion",
        ],
    },

    "Software Engineering": {
        "category": "Technical",
        "subcategory": "Software Engineering",
        "ai_context": (
            "Software Engineering: SDLC models (waterfall, agile, spiral, V-model), "
            "Agile/Scrum, software testing types (unit, integration, system, UAT), "
            "TDD, BDD, version control (Git), CI/CD, UML diagrams, "
            "software quality metrics, code review - "
            "as tested in placement exams."
        ),
        "aliases": [
            "software engineering", "se",
            "software", "software development",
            "sdlc", "software development life cycle",
            "agile", "agile methodology", "agile development",
            "scrum", "scrum framework", "sprint", "kanban",
            "waterfall", "waterfall model", "spiral model", "v model",
            "software testing", "testing",
            "unit testing", "integration testing",
            "system testing", "acceptance testing", "regression testing",
            "tdd", "test driven development", "bdd",
            "git", "version control", "github", "gitlab",
            "ci cd", "ci/cd", "continuous integration", "continuous deployment",
            "devops", "dev ops",
            "uml", "uml diagrams",
        ],
    },

    "System Design": {
        "category": "Technical",
        "subcategory": "System Design",
        "ai_context": (
            "System Design: scalability (horizontal vs vertical), "
            "load balancing, caching (Redis, Memcached, CDN), "
            "database sharding and replication, CAP theorem, "
            "microservices architecture, API gateway, "
            "message queues (Kafka, RabbitMQ), rate limiting, "
            "consistent hashing - as tested in placement exams."
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
            "consistent hashing",
        ],
    },

    "Web Development": {
        "category": "Technical",
        "subcategory": "Web Development",
        "ai_context": (
            "Web Development: HTML5 semantic elements, CSS3 (flexbox, grid, "
            "responsive design), REST APIs, HTTP methods and status codes, "
            "JSON, frontend frameworks (React, Angular, Vue), "
            "backend basics (Node.js/Express, Django, Flask, Spring Boot), "
            "JWT authentication, cookies/sessions - "
            "as tested in placement exams."
        ),
        "aliases": [
            "web development", "web dev", "web programming",
            "html", "html5", "css", "css3",
            "rest", "rest api", "restful", "restful api",
            "api", "apis", "web api",
            "react", "reactjs", "react js",
            "angular", "angularjs",
            "vue", "vuejs", "vue js",
            "express", "expressjs",
            "spring boot", "spring",
            "authentication", "jwt", "json web token",
            "oauth", "sessions", "cookies",
            "frontend", "backend", "full stack", "fullstack",
        ],
    },

    "Cloud Computing": {
        "category": "Technical",
        "subcategory": "Cloud Computing",
        "ai_context": (
            "Cloud Computing: service models (IaaS, PaaS, SaaS), "
            "deployment models (public, private, hybrid, multi-cloud), "
            "AWS core services (EC2, S3, RDS, Lambda), Azure fundamentals, "
            "GCP basics, Docker and containerization, Kubernetes orchestration, "
            "serverless computing, cloud storage - as tested in placement exams."
        ),
        "aliases": [
            "cloud computing", "cloud", "cloud services",
            "aws", "amazon web services",
            "azure", "microsoft azure",
            "gcp", "google cloud",
            "docker", "container", "containers", "containerization",
            "kubernetes", "k8s",
            "serverless", "lambda function aws",
            "iaas", "paas", "saas",
            "virtualization", "hypervisor",
        ],
    },

    "Cybersecurity": {
        "category": "Technical",
        "subcategory": "Cybersecurity",
        "ai_context": (
            "Cybersecurity: cryptography (symmetric: AES, DES; asymmetric: RSA, ECC), "
            "hashing (MD5, SHA-256), digital signatures, PKI, SSL/TLS, "
            "network attacks (SQL injection, XSS, CSRF, MITM, buffer overflow, "
            "phishing, DDoS), firewalls, IDS/IPS, OWASP Top 10 - "
            "as tested in placement exams."
        ),
        "aliases": [
            "cybersecurity", "cyber security", "information security", "infosec",
            "security", "network security",
            "cryptography", "encryption", "decryption",
            "symmetric encryption", "asymmetric encryption",
            "rsa", "aes", "des", "3des",
            "hashing security", "sha", "sha256", "md5",
            "digital signature", "ssl", "tls",
            "firewall", "ids", "ips",
            "sql injection", "xss", "cross site scripting",
            "csrf", "buffer overflow", "phishing", "mitm", "ddos",
            "ethical hacking", "penetration testing", "pen testing",
            "owasp",
        ],
    },

    "Machine Learning": {
        "category": "Technical",
        "subcategory": "Machine Learning",
        "ai_context": (
            "Machine Learning: supervised learning (classification, regression), "
            "unsupervised learning (clustering, PCA), reinforcement learning, "
            "bias-variance tradeoff, overfitting/underfitting, regularization (L1/L2), "
            "cross-validation, algorithms (linear regression, logistic regression, "
            "decision trees, random forest, SVM, KNN, K-means, neural networks) - "
            "as tested in placement exams."
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
            "neural networks", "neural network",
            "deep learning", "cnn", "rnn", "lstm",
            "overfitting", "underfitting", "bias variance",
            "regularization", "cross validation",
            "natural language processing", "nlp",
            "computer vision", "image classification",
            "data science", "data analysis", "data analytics",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Electronics / ECE
    # -------------------------------------------------------------------------

    "Digital Electronics": {
        "category": "Technical",
        "subcategory": "Digital Electronics",
        "ai_context": (
            "Digital Electronics: number systems (binary, octal, hex, BCD), "
            "logic gates (AND, OR, NOT, NAND, NOR, XOR, XNOR), "
            "Boolean algebra, De Morgan's theorem, K-map simplification, "
            "combinational circuits (adder, subtractor, MUX, DEMUX, encoder, decoder), "
            "sequential circuits (flip-flops: SR, JK, D, T; counters, registers), "
            "ADC/DAC - as tested in placement exams."
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
            "Analog Electronics: PN junction diode, Zener diode, "
            "BJT (NPN/PNP, biasing, common emitter/base/collector amplifiers), "
            "FET and MOSFET, op-amp characteristics and applications "
            "(inverting, non-inverting, summing, differentiator, integrator), "
            "oscillators (RC, LC, Colpitts, Hartley), rectifiers, filters, "
            "voltage regulators - as tested in placement exams."
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
            "Signal Processing: signals and systems, Fourier series, "
            "Fourier transform (CTFT, DTFT), Laplace transform, Z-transform, "
            "sampling theorem (Nyquist rate), aliasing, convolution, "
            "DFT and FFT, digital filters (FIR, IIR, Butterworth) - "
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
            "Embedded Systems: microcontroller architecture (8051, PIC, ARM Cortex-M), "
            "peripherals (GPIO, UART, SPI, I2C, PWM, ADC), timers and interrupts, "
            "RTOS concepts (tasks, scheduling, semaphores), "
            "embedded C programming, memory types (ROM, RAM, Flash, EEPROM), "
            "IoT basics - as tested in placement exams."
        ),
        "aliases": [
            "embedded systems", "embedded", "embedded programming",
            "microcontroller", "microcontrollers", "8051", "arm cortex",
            "pic microcontroller", "stm32", "arduino",
            "gpio", "uart", "spi", "i2c", "pwm",
            "rtos", "real time operating system", "freertos",
            "embedded c", "firmware",
            "iot", "internet of things",
        ],
    },

    "VLSI Design": {
        "category": "Technical",
        "subcategory": "VLSI",
        "ai_context": (
            "VLSI Design: CMOS technology (NMOS, PMOS), MOSFET characteristics, "
            "CMOS logic gates design, propagation delay, power dissipation, "
            "FPGA architecture and programming, Verilog HDL (modules, "
            "always blocks, combinational/sequential logic), VHDL basics, "
            "design for testability - as tested in placement exams."
        ),
        "aliases": [
            "vlsi", "vlsi design", "very large scale integration",
            "cmos", "fpga", "verilog", "vhdl",
            "logic design vlsi", "rtl design", "asic",
            "nmos", "pmos",
        ],
    },

    "Communication Systems": {
        "category": "Technical",
        "subcategory": "Communication Systems",
        "ai_context": (
            "Communication Systems: analog modulation (AM, FM, PM), "
            "digital modulation (ASK, FSK, PSK, QAM), multiplexing (TDM, FDM, CDM), "
            "mobile communication (GSM, CDMA, LTE/4G, 5G), "
            "satellite communication, optical fiber communication, "
            "antenna basics, noise and bandwidth, Shannon's theorem - "
            "as tested in placement exams."
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
            "Control Systems: open loop vs closed loop, transfer functions, "
            "block diagram reduction, signal flow graphs (Mason's gain formula), "
            "time response (first order, second order), steady state error, "
            "stability criteria (Routh-Hurwitz, root locus, Bode plot, Nyquist), "
            "PID controllers, state space representation - "
            "as tested in placement exams."
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

    # -------------------------------------------------------------------------
    # TECHNICAL - Electrical (EEE)
    # -------------------------------------------------------------------------

    "Circuit Theory": {
        "category": "Technical",
        "subcategory": "Circuit Theory",
        "ai_context": (
            "Circuit Theory: Ohm's law, KCL, KVL, network theorems "
            "(Thevenin, Norton, Superposition, Maximum Power Transfer, "
            "Millman's, Reciprocity), AC circuits (phasors, impedance, "
            "resonance, power factor), three-phase circuits, "
            "transient analysis (RL, RC, RLC) - as tested in placement exams."
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
            "Power Systems: power generation (thermal, hydro, nuclear, solar, wind), "
            "transmission lines (short/medium/long, ABCD parameters), "
            "distribution systems, load flow analysis (Gauss-Seidel, Newton-Raphson), "
            "fault analysis (symmetrical, unsymmetrical), symmetrical components, "
            "protection (relays, circuit breakers, fuses) - "
            "as tested in placement exams."
        ),
        "aliases": [
            "power systems", "power system", "electrical power",
            "transmission lines", "power transmission",
            "distribution system", "power distribution",
            "load flow", "load flow analysis", "power flow",
            "fault analysis", "symmetrical components", "short circuit",
            "protection", "relay", "circuit breaker", "switchgear",
            "facts", "power quality", "power generation",
        ],
    },

    "Electrical Machines": {
        "category": "Technical",
        "subcategory": "Electrical Machines",
        "ai_context": (
            "Electrical Machines: DC generators (types, EMF equation, characteristics), "
            "DC motors (types, torque, speed control, starting), "
            "transformers (construction, equivalent circuit, efficiency, regulation), "
            "three-phase induction motors (rotating magnetic field, slip, torque-speed), "
            "synchronous generators and motors - as tested in placement exams."
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
            "Power Electronics: power semiconductor devices (diode, thyristor/SCR, "
            "IGBT, power MOSFET), uncontrolled and controlled rectifiers, "
            "inverters (single-phase, three-phase), DC-DC converters (chopper: "
            "Buck, Boost, Buck-Boost), AC voltage controllers, PWM techniques, "
            "SMPS - as tested in placement exams."
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
            "ac voltage controller",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Mechanical (MECH)
    # -------------------------------------------------------------------------

    "Thermodynamics": {
        "category": "Technical",
        "subcategory": "Thermodynamics",
        "ai_context": (
            "Thermodynamics: zeroth, first, second and third laws, "
            "thermodynamic properties (enthalpy, entropy, Gibbs free energy), "
            "ideal gas law, processes (isothermal, adiabatic, isobaric, isochoric), "
            "Carnot cycle, Rankine cycle (steam), Otto cycle (petrol), "
            "Diesel cycle, refrigeration cycles (VCR, absorption) - "
            "as tested in placement exams."
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
            "Fluid Mechanics: fluid properties (viscosity, density, surface tension), "
            "fluid statics (Pascal's law, buoyancy), Bernoulli's equation, "
            "continuity equation, laminar vs turbulent flow, "
            "Reynolds number, flow through pipes (Darcy-Weisbach), "
            "boundary layer, pumps and turbines - "
            "as tested in placement exams."
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
            "Strength of Materials: stress, strain, elastic constants "
            "(E, G, K, Poisson's ratio), stress-strain diagram, "
            "shear force and bending moment diagrams, "
            "bending stress, shear stress in beams, torsion, "
            "deflection of beams (Macaulay's method, Mohr's theorem), "
            "columns (Euler's formula, Rankine's formula) - "
            "as tested in placement exams."
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
            "Manufacturing Technology: casting processes (sand casting, die casting, "
            "investment casting), welding (arc, MIG, TIG, spot, seam), "
            "machining operations (turning, milling, drilling, grinding, "
            "boring, shaping), metal forming (forging, rolling, extrusion, drawing), "
            "powder metallurgy, CNC machining, metrology, quality control (SPC) - "
            "as tested in placement exams."
        ),
        "aliases": [
            "manufacturing", "manufacturing technology", "manufacturing processes",
            "casting", "welding", "machining",
            "turning", "milling", "drilling", "grinding", "boring",
            "cnc", "cnc machining", "cnc programming",
            "metrology", "quality control", "inspection",
            "metal forming", "forging", "rolling", "extrusion", "drawing",
            "powder metallurgy",
        ],
    },

    "Machine Design": {
        "category": "Technical",
        "subcategory": "Machine Design",
        "ai_context": (
            "Machine Design: design process and philosophy, factor of safety, "
            "failure theories (max normal stress, max shear stress, von Mises), "
            "stress concentration, fatigue, fasteners (bolts, screws, rivets), "
            "power screws, shafts and keys, couplings, bearings (rolling and sliding), "
            "gears (spur, helical, bevel, worm), springs, brakes, clutches - "
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

    # -------------------------------------------------------------------------
    # TECHNICAL - Civil
    # -------------------------------------------------------------------------

    "Structural Analysis": {
        "category": "Technical",
        "subcategory": "Structural Analysis",
        "ai_context": (
            "Structural Analysis: types of structures (beams, trusses, frames, arches), "
            "static determinacy, analysis of beams (simply supported, cantilever, "
            "continuous), trusses (method of joints, method of sections), "
            "influence lines, slope deflection method, moment distribution, "
            "matrix stiffness method - as tested in placement exams."
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
            "Geotechnical Engineering: soil classification (IS classification), "
            "Atterberg limits (LL, PL, SL, PI), compaction (Proctor test), "
            "permeability (Darcy's law), seepage, consolidation (Terzaghi), "
            "shear strength (Mohr-Coulomb criterion), bearing capacity "
            "(Terzaghi, Meyerhof), slope stability, retaining walls, "
            "pile foundations - as tested in placement exams."
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
            "Surveying: chain surveying (linear measurements, offsets), "
            "compass surveying (bearings, traversing), levelling (types, "
            "reduced level, contouring), theodolite surveying (horizontal "
            "and vertical angles), tacheometry, total station, GPS/GNSS - "
            "as tested in placement exams."
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
            "Concrete Technology: cement types (OPC, PPC, SRC), hydration, "
            "aggregates (fine, coarse), water-cement ratio, workability "
            "(slump test, Vee-Bee, compaction factor), IS mix design method, "
            "durability, curing methods, admixtures (plasticizers, accelerators), "
            "special concretes (high-strength, self-compacting) - "
            "as tested in placement exams."
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
            "Transportation Engineering: highway planning and alignment, "
            "geometric design (horizontal curves, vertical curves, "
            "sight distance, gradient), pavement design (flexible: CBR method, "
            "rigid: Westergaard method), pavement distresses, "
            "traffic engineering (volume, speed, density, LOS), "
            "railway engineering basics - as tested in placement exams."
        ),
        "aliases": [
            "transportation engineering", "highway engineering",
            "roads", "highways", "road design", "road geometry",
            "pavement design", "flexible pavement", "rigid pavement",
            "traffic engineering", "traffic flow", "los",
            "railway engineering", "railways",
        ],
    },

    # -------------------------------------------------------------------------
    # TECHNICAL - Chemical
    # -------------------------------------------------------------------------

    "Chemical Engineering": {
        "category": "Technical",
        "subcategory": "Chemical Engineering",
        "ai_context": (
            "Chemical Engineering: material and energy balances, "
            "fluid flow (Bernoulli, friction losses), heat transfer "
            "(conduction, convection, radiation, heat exchangers), "
            "mass transfer (distillation, absorption, liquid-liquid extraction), "
            "chemical reaction engineering (batch, CSTR, PFR reactors), "
            "process control and instrumentation - "
            "as tested in placement exams."
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

    # -------------------------------------------------------------------------
    # APTITUDE - Quantitative
    # -------------------------------------------------------------------------

    "Number System": {
        "category": "Aptitude",
        "subcategory": "Number System",
        "ai_context": (
            "Number System aptitude: types of numbers (natural, whole, integer, "
            "rational, irrational), divisibility rules (2,3,4,5,6,7,8,9,10,11), "
            "HCF and LCM (prime factorization method), prime numbers, "
            "unit digit, remainders (Fermat's little theorem), cyclicity - "
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
        ],
    },

    "Percentages": {
        "category": "Aptitude",
        "subcategory": "Percentages",
        "ai_context": (
            "Percentage problems: percentage of a number, "
            "percentage increase and decrease, successive percentage change, "
            "percentage to fraction/decimal conversion, "
            "percentage application in profit/loss/interest - "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "percentages", "percentage", "percent",
            "percentage problems", "percentage increase", "percentage decrease",
            "successive percentage", "percentage change",
        ],
    },

    "Profit and Loss": {
        "category": "Aptitude",
        "subcategory": "Profit & Loss",
        "ai_context": (
            "Profit and Loss: cost price (CP), selling price (SP), "
            "profit percent and loss percent formulas, "
            "marked price, discount, successive discounts, "
            "equivalent discount, dishonest dealer, "
            "partnership profit sharing - "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "profit and loss", "profit & loss", "profit loss",
            "profit", "loss", "profit percent", "loss percent",
            "discount", "marked price", "selling price", "cost price",
            "successive discounts", "trade discount", "equivalent discount",
        ],
    },

    "Simple and Compound Interest": {
        "category": "Aptitude",
        "subcategory": "Simple & Compound Interest",
        "ai_context": (
            "Simple Interest (SI = PRT/100) and Compound Interest "
            "(A = P(1+r/n)^nt): difference between SI and CI, "
            "half-yearly/quarterly/monthly compounding, "
            "effective rate of interest, population growth, "
            "depreciation problems - "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "simple interest", "compound interest",
            "simple and compound interest", "si ci",
            "si", "ci", "interest problems", "interest",
            "half yearly compounding", "quarterly compounding",
            "effective rate", "population growth", "depreciation",
        ],
    },

    "Time and Work": {
        "category": "Aptitude",
        "subcategory": "Time & Work",
        "ai_context": (
            "Time and Work: work done formula (work = efficiency x time), "
            "combined work rate, LCM method, "
            "A and B together complete work, "
            "pipes and cisterns (filling/draining), "
            "work and wages - "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "time and work", "work and time", "work problems",
            "work", "efficiency work",
            "pipes and cisterns", "pipes cisterns",
            "pipes", "cisterns", "cistern", "tank filling",
            "tap", "inlet", "outlet pipe",
            "work and wages",
        ],
    },

    "Time Speed Distance": {
        "category": "Aptitude",
        "subcategory": "Time Speed Distance",
        "ai_context": (
            "Time, Speed and Distance: speed = distance/time, "
            "relative speed (same direction: difference, opposite: sum), "
            "average speed (2S1S2/(S1+S2)), trains crossing problems "
            "(pole, platform, each other), boats and streams "
            "(upstream speed = u-v, downstream = u+v), races - "
            "as tested in placement aptitude exams."
        ),
        "aliases": [
            "time speed distance", "speed distance time", "speed and distance",
            "speed", "distance time", "tsd",
            "relative speed",
            "trains", "train problems", "train crossing",
            "boats and streams", "boats", "boat", "streams", "stream",
            "upstream", "downstream", "speed of stream",
            "average speed", "races",
        ],
    },

    "Ratio and Proportion": {
        "category": "Aptitude",
        "subcategory": "Ratio & Proportion",
        "ai_context": (
            "Ratio and Proportion: ratio in simplest form, "
            "compounded ratio, duplicate/triplicate ratio, "
            "proportion (direct and inverse), continued proportion, "
            "variation, partnership problems - "
            "as tested in placement aptitude exams."
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
            "Mixtures and Alligation: alligation method (weighted average), "
            "mixing two items of different prices or concentrations, "
            "repeated dilution (milk-water problems), "
            "mean price, rule of alligation - "
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
            "Average: arithmetic mean, weighted average, "
            "average of consecutive numbers, "
            "effect of including/excluding a number, "
            "average speed, age-based average problems - "
            "as tested in placement aptitude exams."
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
            "Permutations and Combinations: factorial notation, "
            "nPr (arrangements), nCr (selections), "
            "circular permutation, repeated objects, "
            "word arrangement problems, selection of teams/committees, "
            "distribution problems - "
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
            "Probability: sample space, events, classical probability, "
            "complementary events (P(A') = 1 - P(A)), "
            "mutually exclusive events, independent events, "
            "conditional probability, Bayes' theorem, "
            "problems on dice, cards (deck of 52), coins - "
            "as tested in placement aptitude exams."
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
            "Problems on Ages: calculating present age, past age, future age, "
            "ratio of ages at different points in time, "
            "algebraic equations for ages, "
            "average age problems - "
            "as tested in placement aptitude exams."
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
            "Data Interpretation: reading bar charts (simple and grouped), "
            "pie charts (percentage and value), line graphs (trends), "
            "tables, mixed graphs; percentage calculation from graphs, "
            "ratio comparison, data sufficiency basics - "
            "as tested in placement aptitude exams."
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
            "Logical Reasoning: number series (find the missing term), "
            "letter series, coding-decoding (letter shift, number coding), "
            "blood relations (family tree), direction sense (final position), "
            "seating arrangement (linear and circular), "
            "syllogisms (all/some/no statements), puzzles, "
            "clock and calendar, statement conclusions - "
            "as tested in placement aptitude exams."
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

    # -------------------------------------------------------------------------
    # VERBAL
    # -------------------------------------------------------------------------

    "Grammar": {
        "category": "Verbal",
        "subcategory": "Grammar",
        "ai_context": (
            "English Grammar for placement exams: all 12 tenses with usage rules, "
            "subject-verb agreement, articles (a/an/the), prepositions, "
            "conjunctions (coordinating, subordinating), active and passive voice "
            "transformation, direct and indirect speech (narration), "
            "question tags, conditionals (zero, first, second, third) - "
            "as tested in placement verbal exams."
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
            "Vocabulary for placement exams: synonyms (words with similar meaning), "
            "antonyms (words with opposite meaning), contextual word usage, "
            "one-word substitution (a single word for a phrase), "
            "idioms and phrases (meaning and usage), "
            "commonly confused words (affect/effect, accept/except), "
            "verbal analogies - as tested in placement verbal exams."
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
            "Reading Comprehension for placement exams: passage-based questions, "
            "identifying the main idea, inferential questions, "
            "vocabulary in context, author's tone and purpose "
            "(critical, humorous, sarcastic, objective, subjective), "
            "true/false based on passage, title selection - "
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
            "Sentence Correction for placement exams: spotting grammatical errors "
            "(subject-verb agreement, tense errors, pronoun errors, article errors, "
            "preposition errors), sentence improvement (choosing the correct option "
            "to replace underlined part), fill in the blanks (choosing the most "
            "appropriate word), cloze test - as tested in placement verbal exams."
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
            "Para Jumbles for placement exams: rearranging jumbled sentences "
            "to form a coherent and logical paragraph; "
            "finding the opening sentence (topic sentence), "
            "connecting sentences using transition words, "
            "finding the concluding sentence - "
            "as tested in placement verbal exams."
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
            "Soft Skills and Communication for placement: effective communication "
            "(verbal, non-verbal, written), group discussion tips, "
            "interpersonal skills, teamwork, leadership, "
            "time management, problem-solving, adaptability, "
            "email and professional writing etiquette - "
            "as tested in placement behavioral rounds."
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
# SECTION 2 - BUILD LOOKUP INDEX (runs once at import time)
# alias (lowercase) -> canonical name
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
# SECTION 3 - PURE NOISE / GARBAGE
# ===========================================================================

_NOISE = {
    # Single letters that are NOT valid topics
    # NOTE: "c" is excluded here because "C" is a programming language
    "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "t", "u", "v", "w", "x", "y", "z",
    "hello", "hi", "hey", "ok", "okay", "yes", "no", "yep", "nope",
    "what", "how", "why", "when", "where", "who", "which",
    "this", "that", "these", "those", "is", "are", "was", "were",
    "good", "bad", "easy", "hard", "difficult",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "test", "quiz", "exam", "question", "answer",
    "abc", "xyz", "asdf", "qwerty", "aaa", "bbb", "ccc",
    "lol", "idk", "omg", "wtf", "lmao",
}


# ===========================================================================
# SECTION 4 - VALIDITY CHECK
# ===========================================================================

_GIBBERISH = re.compile(r'(.)\1{3,}|^[\W\d]+$', re.I)


_SINGLE_LETTER_TOPICS = {"c", "a"}  # valid single-letter topics

def _is_valid_query(text: str) -> bool:
    """Return True if the string is worth trying to resolve."""
    clean = text.strip().lower()

    if len(clean.replace(' ', '')) < 1:
        return False

    if not re.search(r'[a-zA-Z]', clean):
        return False

    if clean in _NOISE:
        return False

    # Allow known single-letter topics
    if clean in _SINGLE_LETTER_TOPICS:
        return True

    # Allow short known acronyms (2-4 chars all letters) if in alias index
    if len(clean) <= 4 and clean.isalpha() and clean in _ALIAS_INDEX:
        return True

    if len(clean.replace(' ', '')) < 2:
        return False

    for word in re.split(r'[\s\-/&]+', clean):
        word = word.strip('.,;:')
        if len(word) <= 2:
            continue
        if _GIBBERISH.search(word):
            return False
        letters = [c for c in word if c.isalpha()]
        if len(letters) > 4:
            vowels = sum(1 for c in letters if c in 'aeiou')
            if vowels / len(letters) < 0.1:
                return False

    return True


# ===========================================================================
# SECTION 5 - CORE RESOLVER
# ===========================================================================

def _make_result(canonical: str) -> dict:
    """Build a 'single' result dict from a canonical topic name."""
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
    Resolve a user search query to a canonical placement topic.

    Returns one of:
        { status: 'single',  topic, canonical, subtopic, category,
                             ai_context, display_label }
        { status: 'multi',   options: [...], query }
        { status: 'new',     topic, ai_context }
        { status: 'invalid', message }
    """
    raw   = user_input.strip()
    clean = re.sub(r'\s+', ' ', raw.lower()).strip()

    # 1. Basic validity
    if not _is_valid_query(clean):
        if len(clean.replace(' ', '')) < 2:
            return {"status": "invalid", "message": "Please type at least 2 characters."}
        return {
            "status":  "invalid",
            "message": (
                f'"{raw}" doesn\'t look like a placement topic. '
                'Try something like "sorting algorithms", "SQL joins", '
                '"boats and streams", or "reading comprehension".'
            ),
        }

    # 2. Exact alias match
    hit = _ALIAS_INDEX.get(clean)
    if hit:
        if hit.startswith("__MULTI__"):
            canons = [c for c in hit[len("__MULTI__"):].split("||")
                      if c in CANONICAL_TOPICS]
            options = [_make_result(c) for c in canons]
            return {"status": "multi", "options": options, "query": raw}
        return _make_result(hit)

    # 3. Prefix match (query is prefix of an alias, min 4 chars)
    if len(clean) >= 4:
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

    # 4. Substring match (alias contains the query, min 5 chars)
    if len(clean) >= 5:
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

    # 5. Genuinely new topic
    title_cased = raw.title()
    return {
        "status":     "new",
        "topic":      title_cased,
        "ai_context": (
            f"{title_cased} — core concepts, theory, and applied problems "
            f"as tested in engineering placement exams and technical interviews."
        ),
    }


# ===========================================================================
# SECTION 6 - AI CONTEXT BUILDER
# ===========================================================================

def build_ai_context(topic: str, subtopic: str, ai_context: str = '') -> str:
    """Compose the context string injected into the AI prompt."""
    if ai_context:
        first_word = subtopic.split()[0] if subtopic else topic.split()[0]
        return (
            f"Topic: {topic}\n"
            f"Subtopic: {subtopic}\n"
            f"Context: Generate questions ONLY about: {ai_context}\n"
            f"Do NOT generate questions about the literal/everyday meaning of "
            f'"{first_word}" - focus strictly on the placement exam context above.'
        )
    return f"Topic: {topic}\nSubtopic: {subtopic if subtopic else topic}"


# ===========================================================================
# SECTION 7 - QUICK SELF-TEST
# ===========================================================================

if __name__ == "__main__":
    tests = [
        # Technical - languages
        "c", "java", "python", "cpp", "golang", "js", "sql",
        # Technical - CS core
        "dsa", "os", "dbms", "cn", "oop",
        "dp", "greedy", "bst", "heap", "bfs", "dfs",
        "dijkstra", "sorting", "binary search",
        "normalization", "bcnf", "joins", "inner join",
        "acid", "indexing",
        "deadlock", "paging", "semaphore", "round robin",
        "osi", "tcp", "dns", "subnetting",
        "design patterns", "singleton", "solid",
        "system design", "microservices", "kafka",
        "agile", "sdlc", "git",
        "machine learning", "nlp", "cnn",
        "docker", "kubernetes",
        # ECE/EEE
        "vlsi", "verilog", "fpga",
        "op amp", "bjt", "mosfet",
        "pid", "root locus", "bode",
        # MECH
        "thermodynamics", "bernoulli", "som",
        # CIVIL
        "rcc", "geotechnical", "surveying",
        # Aptitude
        "hcf", "percentage", "profit",
        "si ci", "pipes", "trains", "boats",
        "permutation", "probability", "syllogism",
        "seating", "blood relation", "coding decoding",
        "data interpretation", "bar chart",
        # Verbal
        "grammar", "synonyms", "comprehension",
        "error detection", "para jumbles", "soft skills",
        # Prefix matches
        "sort", "sorti", "perm", "prob",
        "boat", "encap", "inherit",
        # Invalid
        "aaaa", "1234", "hello", "xyz", "qwerty",
        # New
        "quantum computing", "blockchain",
    ]

    print(f"\n{'─'*75}")
    print(f"{'QUERY':<35} {'STATUS':<10} RESULT")
    print(f"{'─'*75}")
    for q in tests:
        r = resolve_topic(q)
        st = r["status"]
        if st == "single":
            detail = r["canonical"]
        elif st == "multi":
            detail = "MULTI: " + " | ".join(o["canonical"] for o in r["options"][:3])
        elif st == "new":
            detail = "NEW: " + r["topic"]
        else:
            detail = "INVALID"
        print(f"{q:<35} {st:<10} {detail}")
    print(f"{'─'*75}\n")