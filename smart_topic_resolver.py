"""
smart_topic_resolver.py
========================
Handles all smart topic resolution logic:
- Keyword → canonical topic/subtopic mapping (Boats → Boats and Streams)
- Multi-topic detection (Recursion → Algorithms, C, Java, Python)
- Genuinely new topic detection
- Invalid/garbage input rejection
- Context-aware AI prompt generation

Add this file to your project root. Import in app.py:
    from smart_topic_resolver import resolve_topic, build_ai_context
"""

import re

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: ALIAS MAP
# keyword (lowercase) → (topic, subtopic, description_for_ai)
# When a user types something, we check if it matches any alias.
# ═══════════════════════════════════════════════════════════════════════════

ALIAS_MAP = {
    # ── APTITUDE: Speed / Distance / Time ─────────────────────────────────
    'boats':               ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),
    'boat':                ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),
    'boats and streams':   ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),
    'stream':              ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),
    'upstream':            ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),
    'downstream':          ('Quantitative Aptitude', 'Boats and Streams',    'upstream downstream problems, speed of boat in still water, speed of current'),

    'trains':              ('Quantitative Aptitude', 'Trains',               'time taken by trains to cross each other, platforms, poles; relative speed'),
    'train problems':      ('Quantitative Aptitude', 'Trains',               'time taken by trains to cross each other, platforms, poles; relative speed'),

    'pipes':               ('Quantitative Aptitude', 'Pipes and Cisterns',   'filling and emptying tanks, time taken, combined work rate of pipes'),
    'cisterns':            ('Quantitative Aptitude', 'Pipes and Cisterns',   'filling and emptying tanks, time taken, combined work rate of pipes'),
    'pipes and cisterns':  ('Quantitative Aptitude', 'Pipes and Cisterns',   'filling and emptying tanks, time taken, combined work rate of pipes'),
    'tank':                ('Quantitative Aptitude', 'Pipes and Cisterns',   'filling and emptying tanks, time taken, combined work rate of pipes'),

    'profit':              ('Quantitative Aptitude', 'Profit & Loss',        'cost price, selling price, profit percent, loss percent, discount, markup'),
    'loss':                ('Quantitative Aptitude', 'Profit & Loss',        'cost price, selling price, profit percent, loss percent, discount, markup'),
    'profit and loss':     ('Quantitative Aptitude', 'Profit & Loss',        'cost price, selling price, profit percent, loss percent, discount, markup'),
    'discount':            ('Quantitative Aptitude', 'Profit & Loss',        'cost price, selling price, profit percent, loss percent, discount, markup'),

    'simple interest':     ('Quantitative Aptitude', 'Simple & Compound Interest', 'SI and CI formulas, principal, rate, time, difference between SI and CI'),
    'compound interest':   ('Quantitative Aptitude', 'Simple & Compound Interest', 'SI and CI formulas, principal, rate, time, difference between SI and CI'),
    'si':                  ('Quantitative Aptitude', 'Simple & Compound Interest', 'SI and CI formulas, principal, rate, time, difference between SI and CI'),
    'ci':                  ('Quantitative Aptitude', 'Simple & Compound Interest', 'SI and CI formulas, principal, rate, time, difference between SI and CI'),
    'interest':            ('Quantitative Aptitude', 'Simple & Compound Interest', 'SI and CI formulas, principal, rate, time, difference between SI and CI'),

    'percentage':          ('Quantitative Aptitude', 'Percentages',          'percentage calculations, percentage increase/decrease, successive percentage'),
    'percent':             ('Quantitative Aptitude', 'Percentages',          'percentage calculations, percentage increase/decrease, successive percentage'),

    'ratio':               ('Quantitative Aptitude', 'Ratio & Proportion',   'ratios, proportions, direct/inverse proportion, partnership problems'),
    'proportion':          ('Quantitative Aptitude', 'Ratio & Proportion',   'ratios, proportions, direct/inverse proportion, partnership problems'),

    'average':             ('Quantitative Aptitude', 'Average',              'mean, weighted average, average speed, age-based average problems'),
    'mean':                ('Quantitative Aptitude', 'Average',              'mean, weighted average, average speed, age-based average problems'),

    'time and work':       ('Quantitative Aptitude', 'Time & Work',          'work done, efficiency, days to complete work alone or together, LCM method'),
    'work':                ('Quantitative Aptitude', 'Time & Work',          'work done, efficiency, days to complete work alone or together, LCM method'),

    'speed':               ('Quantitative Aptitude', 'Time Speed Distance',  'speed distance time formula, relative speed, average speed, races'),
    'distance':            ('Quantitative Aptitude', 'Time Speed Distance',  'speed distance time formula, relative speed, average speed, races'),
    'time speed distance': ('Quantitative Aptitude', 'Time Speed Distance',  'speed distance time formula, relative speed, average speed, races'),

    'permutation':         ('Quantitative Aptitude', 'Permutations & Combinations', 'nPr, nCr, arrangements, selections, word arrangements, circular permutation'),
    'combination':         ('Quantitative Aptitude', 'Permutations & Combinations', 'nPr, nCr, arrangements, selections, word arrangements, circular permutation'),
    'pnc':                 ('Quantitative Aptitude', 'Permutations & Combinations', 'nPr, nCr, arrangements, selections, word arrangements, circular permutation'),

    'probability':         ('Quantitative Aptitude', 'Probability',          'classical probability, events, sample space, conditional probability, dice/cards/coins'),

    'mixture':             ('Quantitative Aptitude', 'Mixtures & Alligations', 'alligation method, mixing two items of different prices/concentrations'),
    'alligation':          ('Quantitative Aptitude', 'Mixtures & Alligations', 'alligation method, mixing two items of different prices/concentrations'),

    'number system':       ('Quantitative Aptitude', 'Number System',        'divisibility rules, HCF, LCM, prime numbers, remainders, unit digit'),
    'hcf':                 ('Quantitative Aptitude', 'Number System',        'HCF and LCM problems, finding GCD, applications in real problems'),
    'lcm':                 ('Quantitative Aptitude', 'Number System',        'HCF and LCM problems, finding GCD, applications in real problems'),
    'prime':               ('Quantitative Aptitude', 'Number System',        'prime numbers, divisibility, factors, prime factorization'),

    'ages':                ('Quantitative Aptitude', 'Problems on Ages',     'present/past/future age calculations, ratio of ages, algebra-based age problems'),
    'age':                 ('Quantitative Aptitude', 'Problems on Ages',     'present/past/future age calculations, ratio of ages, algebra-based age problems'),
    'problems on ages':    ('Quantitative Aptitude', 'Problems on Ages',     'present/past/future age calculations, ratio of ages, algebra-based age problems'),

    'partnership':         ('Quantitative Aptitude', 'Partnership',          'capital invested, profit sharing, sleeping vs working partner, time-weighted capital'),

    'calendar':            ('Logical Reasoning',     'Calendar',             'day of week calculation, odd days method, leap year rules'),
    'clock':               ('Logical Reasoning',     'Clocks',               'angle between hands, time calculations, fast/slow clocks'),
    'clocks':              ('Logical Reasoning',     'Clocks',               'angle between hands, time calculations, fast/slow clocks'),

    'blood relation':      ('Logical Reasoning',     'Blood Relations',      'family tree, relationships, coded blood relations'),
    'blood relations':     ('Logical Reasoning',     'Blood Relations',      'family tree, relationships, coded blood relations'),
    'family':              ('Logical Reasoning',     'Blood Relations',      'family tree, relationships, coded blood relations'),

    'seating':             ('Logical Reasoning',     'Seating Arrangement',  'linear, circular, rectangular arrangement puzzles'),
    'seating arrangement': ('Logical Reasoning',     'Seating Arrangement',  'linear, circular, rectangular arrangement puzzles'),

    'coding decoding':     ('Logical Reasoning',     'Coding-Decoding',      'letter/number coding, pattern finding, reverse coding'),
    'coding':              ('Logical Reasoning',     'Coding-Decoding',      'letter/number coding, pattern finding, reverse coding'),

    'syllogism':           ('Logical Reasoning',     'Syllogisms',           'Venn diagram method, all/some/no statements, conclusions'),
    'syllogisms':          ('Logical Reasoning',     'Syllogisms',           'Venn diagram method, all/some/no statements, conclusions'),

    'direction':           ('Logical Reasoning',     'Direction Sense',      'compass directions, distance from starting point, turns'),
    'direction sense':     ('Logical Reasoning',     'Direction Sense',      'compass directions, distance from starting point, turns'),

    'series':              ('Logical Reasoning',     'Number Series',        'missing number in series, letter series, alphanumeric series'),
    'number series':       ('Logical Reasoning',     'Number Series',        'missing number in series, letter series, alphanumeric series'),
    'pattern':             ('Logical Reasoning',     'Number Series',        'missing number in series, letter series, alphanumeric series'),

    'puzzle':              ('Logical Reasoning',     'Puzzles',              'logical puzzles, grid-based puzzles, constraint satisfaction'),
    'puzzles':             ('Logical Reasoning',     'Puzzles',              'logical puzzles, grid-based puzzles, constraint satisfaction'),

    # ── VERBAL ────────────────────────────────────────────────────────────
    'synonym':             ('Verbal Ability', 'Synonyms & Antonyms',   'words with similar meaning, choosing correct synonym from options'),
    'antonym':             ('Verbal Ability', 'Synonyms & Antonyms',   'words with opposite meaning, choosing correct antonym from options'),
    'synonyms':            ('Verbal Ability', 'Synonyms & Antonyms',   'words with similar meaning, choosing correct synonym from options'),
    'antonyms':            ('Verbal Ability', 'Synonyms & Antonyms',   'words with opposite meaning, choosing correct antonym from options'),
    'vocabulary':          ('Verbal Ability', 'Synonyms & Antonyms',   'word meanings, synonyms, antonyms, contextual vocabulary'),

    'reading comprehension':('Verbal Ability','Reading Comprehension', 'passage-based questions, inference, main idea, author tone'),
    'comprehension':       ('Verbal Ability', 'Reading Comprehension', 'passage-based questions, inference, main idea, author tone'),
    'passage':             ('Verbal Ability', 'Reading Comprehension', 'passage-based questions, inference, main idea, author tone'),

    'fill in the blank':   ('Verbal Ability', 'Fill in the Blanks',    'choosing correct word/phrase to complete sentence, prepositions, articles'),
    'fill in blanks':      ('Verbal Ability', 'Fill in the Blanks',    'choosing correct word/phrase to complete sentence, prepositions, articles'),
    'blanks':              ('Verbal Ability', 'Fill in the Blanks',    'choosing correct word/phrase to complete sentence, prepositions, articles'),

    'error':               ('Verbal Ability', 'Error Detection',       'spotting grammatical errors in sentences, subject-verb agreement, tense errors'),
    'error detection':     ('Verbal Ability', 'Error Detection',       'spotting grammatical errors in sentences, subject-verb agreement, tense errors'),
    'spot the error':      ('Verbal Ability', 'Error Detection',       'spotting grammatical errors in sentences, subject-verb agreement, tense errors'),

    'para jumble':         ('Verbal Ability', 'Para Jumbles',          'rearranging sentences to form coherent paragraph, finding correct order'),
    'para jumbles':        ('Verbal Ability', 'Para Jumbles',          'rearranging sentences to form coherent paragraph, finding correct order'),
    'sentence order':      ('Verbal Ability', 'Para Jumbles',          'rearranging sentences to form coherent paragraph, finding correct order'),

    'idiom':               ('Verbal Ability', 'Idioms & Phrases',      'meaning of idiomatic expressions, usage in sentences'),
    'idioms':              ('Verbal Ability', 'Idioms & Phrases',      'meaning of idiomatic expressions, usage in sentences'),
    'phrase':              ('Verbal Ability', 'Idioms & Phrases',      'meaning of idiomatic expressions, usage in sentences'),

    'one word':            ('Verbal Ability', 'One Word Substitution', 'single word for a given phrase or definition'),
    'one word substitution':('Verbal Ability','One Word Substitution', 'single word for a given phrase or definition'),

    'grammar':             ('Verbal Ability', 'Grammar',               'tenses, articles, prepositions, conjunctions, subject-verb agreement, voice, narration'),
    'tense':               ('Verbal Ability', 'Grammar',               'all tenses: simple, continuous, perfect, perfect continuous; usage rules'),
    'tenses':              ('Verbal Ability', 'Grammar',               'all tenses: simple, continuous, perfect, perfect continuous; usage rules'),
    'preposition':         ('Verbal Ability', 'Grammar',               'use of prepositions: in, on, at, by, with, for, since, until'),
    'voice':               ('Verbal Ability', 'Grammar',               'active and passive voice transformation rules'),
    'narration':           ('Verbal Ability', 'Grammar',               'direct and indirect speech conversion rules'),
    'speech':              ('Verbal Ability', 'Grammar',               'direct and indirect speech conversion rules'),

    'sentence improvement':('Verbal Ability', 'Sentence Improvement',  'identifying incorrect part of sentence and choosing correct replacement'),
    'sentence correction': ('Verbal Ability', 'Sentence Improvement',  'identifying incorrect part of sentence and choosing correct replacement'),

    'analogy':             ('Verbal Ability', 'Analogies',             'word relationship pairs, completing analogies, verbal analogies'),
    'analogies':           ('Verbal Ability', 'Analogies',             'word relationship pairs, completing analogies, verbal analogies'),

    # ── TECHNICAL: Multi-topic keywords (handled separately) ──────────────
    # These appear under multiple topics — handled in MULTI_TOPIC_MAP below.

    # ── TECHNICAL: Algorithms ─────────────────────────────────────────────
    'dynamic programming': ('Algorithms', 'Dynamic Programming',      'memoization, tabulation, overlapping subproblems, optimal substructure, classic DP problems'),
    'dp':                  ('Algorithms', 'Dynamic Programming',      'memoization, tabulation, overlapping subproblems, optimal substructure, classic DP problems'),
    'greedy':              ('Algorithms', 'Greedy Algorithms',        'greedy choice property, activity selection, fractional knapsack, Huffman coding'),
    'greedy algorithm':    ('Algorithms', 'Greedy Algorithms',        'greedy choice property, activity selection, fractional knapsack, Huffman coding'),
    'backtracking':        ('Algorithms', 'Backtracking',             'N-queens, Sudoku solver, subset sum, permutations using backtracking'),
    'divide and conquer':  ('Algorithms', 'Divide & Conquer',         'merge sort, quick sort, binary search, Strassen matrix multiplication'),
    'graph algorithm':     ('Algorithms', 'Graph Algorithms',         'BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Prim, Kruskal'),
    'graph algorithms':    ('Algorithms', 'Graph Algorithms',         'BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Prim, Kruskal'),
    'dijkstra':            ('Algorithms', 'Graph Algorithms',         "Dijkstra's shortest path algorithm, priority queue, weighted graphs"),
    'sorting':             ('Algorithms', 'Sorting Algorithms',       'bubble, selection, insertion, merge, quick, heap sort; time complexity comparison'),
    'searching':           ('Algorithms', 'Searching Algorithms',     'linear search, binary search, interpolation search, time complexity'),
    'binary search':       ('Algorithms', 'Searching Algorithms',     'binary search algorithm, conditions, time complexity O(log n), variants'),
    'complexity':          ('Algorithms', 'Time Complexity',          'Big O notation, best/average/worst case, space complexity, amortized analysis'),
    'big o':               ('Algorithms', 'Time Complexity',          'Big O notation, best/average/worst case, space complexity, amortized analysis'),
    'time complexity':     ('Algorithms', 'Time Complexity',          'Big O notation, best/average/worst case, space complexity, amortized analysis'),

    # ── TECHNICAL: Data Structures ────────────────────────────────────────
    'linked list':         ('Data Structures', 'Linked Lists',        'singly, doubly, circular linked lists; insertion, deletion, reversal'),
    'doubly linked list':  ('Data Structures', 'Linked Lists',        'doubly linked list operations, prev/next pointers, advantages over singly'),
    'stack':               ('Data Structures', 'Stacks',              'LIFO, push, pop, peek, infix/postfix conversion, balanced parentheses'),
    'queue':               ('Data Structures', 'Queues',              'FIFO, enqueue, dequeue, circular queue, priority queue, deque'),
    'binary tree':         ('Data Structures', 'Trees (Binary, BST)', 'binary tree traversals, BST operations, height, diameter, balanced trees'),
    'bst':                 ('Data Structures', 'Trees (Binary, BST)', 'binary search tree, insert/delete/search, inorder gives sorted output'),
    'binary search tree':  ('Data Structures', 'Trees (Binary, BST)', 'binary search tree, insert/delete/search, inorder gives sorted output'),
    'heap':                ('Data Structures', 'Heaps',               'min heap, max heap, heapify, heap sort, priority queue implementation'),
    'hashing':             ('Data Structures', 'Hashing',             'hash functions, collision resolution, chaining, open addressing, load factor'),
    'hash table':          ('Data Structures', 'Hashing',             'hash tables, hash maps, collision handling, time complexity O(1) average'),
    'graph':               ('Data Structures', 'Graphs',              'directed/undirected graphs, adjacency matrix/list, BFS, DFS, connected components'),
    'trie':                ('Data Structures', 'Tries',               'prefix tree, insert/search/delete in trie, autocomplete, word problems'),

    # ── TECHNICAL: OS ─────────────────────────────────────────────────────
    'deadlock':            ('OS', 'Deadlock',                         'deadlock conditions, prevention, avoidance (Banker algorithm), detection, recovery'),
    'banker algorithm':    ('OS', 'Deadlock',                         "Banker's algorithm for deadlock avoidance, safe state, resource allocation"),
    'scheduling':          ('OS', 'CPU Scheduling',                   'FCFS, SJF, Round Robin, Priority scheduling, Gantt charts, turnaround time'),
    'cpu scheduling':      ('OS', 'CPU Scheduling',                   'FCFS, SJF, Round Robin, Priority scheduling, Gantt charts, turnaround time'),
    'round robin':         ('OS', 'CPU Scheduling',                   'Round Robin scheduling, time quantum, context switching, preemptive scheduling'),
    'paging':              ('OS', 'Memory Management',                'paging, page table, page fault, TLB, frame allocation, demand paging'),
    'page fault':          ('OS', 'Memory Management',                'page fault handling, page replacement algorithms: LRU, FIFO, Optimal'),
    'virtual memory':      ('OS', 'Virtual Memory',                   'virtual memory concept, demand paging, thrashing, working set model'),
    'thrashing':           ('OS', 'Virtual Memory',                   'thrashing, cause, prevention using working set model and page fault frequency'),
    'semaphore':           ('OS', 'Synchronization',                  'semaphores, mutex, binary semaphore, counting semaphore, producer-consumer problem'),
    'mutex':               ('OS', 'Synchronization',                  'mutex locks, critical section, race condition, monitor, synchronization problems'),
    'process':             ('OS', 'Process Management',               'process states, PCB, context switching, fork, process creation/termination'),
    'thread':              ('OS', 'Threads',                          'multithreading, user/kernel threads, thread synchronization, benefits'),

    # ── TECHNICAL: DBMS ───────────────────────────────────────────────────
    'normalization':       ('DBMS', 'Normalization',                  '1NF, 2NF, 3NF, BCNF, functional dependencies, anomalies, decomposition'),
    'bcnf':                ('DBMS', 'Normalization',                  'Boyce-Codd Normal Form, when 3NF is not sufficient, lossless decomposition'),
    'join':                ('DBMS', 'Joins',                          'INNER JOIN, LEFT/RIGHT/FULL OUTER JOIN, CROSS JOIN, NATURAL JOIN, self join'),
    'joins':               ('DBMS', 'Joins',                          'INNER JOIN, LEFT/RIGHT/FULL OUTER JOIN, CROSS JOIN, NATURAL JOIN, self join'),
    'transaction':         ('DBMS', 'Transactions & ACID',            'ACID properties, commit, rollback, savepoint, isolation levels, concurrency control'),
    'acid':                ('DBMS', 'Transactions & ACID',            'Atomicity, Consistency, Isolation, Durability; transaction management'),
    'indexing':            ('DBMS', 'Indexing',                       'B-tree index, clustered/non-clustered index, index scan vs table scan, query optimization'),
    'sql':                 ('DBMS', 'SQL Queries',                    'SELECT, INSERT, UPDATE, DELETE, GROUP BY, HAVING, ORDER BY, subqueries, aggregate functions'),
    'trigger':             ('DBMS', 'Views & Triggers',               'SQL triggers, BEFORE/AFTER triggers, use cases, views vs materialized views'),
    'view':                ('DBMS', 'Views & Triggers',               'SQL views, creating/updating views, advantages, differences from tables'),

    # ── TECHNICAL: Networks ───────────────────────────────────────────────
    'osi model':           ('Computer Networks', 'OSI Model',         '7 layers of OSI, functions of each layer, protocols at each layer'),
    'tcp ip':              ('Computer Networks', 'TCP/IP Model',      'TCP/IP 4-layer model, comparison with OSI, protocols: TCP, UDP, IP, HTTP'),
    'tcp':                 ('Computer Networks', 'TCP/IP Model',      'TCP vs UDP, 3-way handshake, connection establishment, reliable transmission'),
    'udp':                 ('Computer Networks', 'TCP/IP Model',      'UDP protocol, connectionless, use cases: DNS, streaming, gaming'),
    'subnetting':          ('Computer Networks', 'Subnetting',        'subnet mask, CIDR notation, number of hosts, network address calculation'),
    'ip addressing':       ('Computer Networks', 'IP Addressing',     'IPv4, IPv6, classes A/B/C/D/E, private IP ranges, NAT'),
    'dns':                 ('Computer Networks', 'Application Layer', 'DNS resolution, authoritative servers, DNS records: A, MX, CNAME, TTL'),
    'http':                ('Computer Networks', 'Application Layer', 'HTTP methods GET/POST/PUT/DELETE, status codes, HTTPS, cookies, sessions'),
    'routing':             ('Computer Networks', 'Routing Protocols', 'RIP, OSPF, BGP, distance vector vs link state, routing table'),

    # ── TECHNICAL: OOP / Design ───────────────────────────────────────────
    'design pattern':      ('OOP', 'Design Patterns',                 'Singleton, Factory, Observer, Strategy, Decorator, MVC; GoF patterns'),
    'design patterns':     ('OOP', 'Design Patterns',                 'Singleton, Factory, Observer, Strategy, Decorator, MVC; GoF patterns'),
    'solid':               ('OOP', 'SOLID Principles',                'Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion'),
    'singleton':           ('OOP', 'Design Patterns',                 'Singleton pattern, thread safety, lazy vs eager initialization'),
    'factory':             ('OOP', 'Design Patterns',                 'Factory and Abstract Factory patterns, object creation without specifying class'),
    'inheritance':         ('OOP', 'Inheritance',                     'single, multiple, multilevel inheritance; method overriding, super keyword'),
    'polymorphism':        ('OOP', 'Polymorphism',                    'compile-time (overloading) and runtime (overriding) polymorphism, virtual functions'),
    'encapsulation':       ('OOP', 'Encapsulation',                   'data hiding, getters/setters, access modifiers, benefits of encapsulation'),
    'abstraction':         ('OOP', 'Abstraction',                     'abstract classes, interfaces, hiding implementation details'),

    # ── ML / AI ───────────────────────────────────────────────────────────
    'neural network':      ('Python', 'Machine Learning Basics',      'perceptron, layers, activation functions, forward/backpropagation, gradient descent'),
    'machine learning':    ('Python', 'Machine Learning Basics',      'supervised, unsupervised, reinforcement learning; overfitting, bias-variance tradeoff'),
    'regression':          ('Python', 'Machine Learning Basics',      'linear regression, logistic regression, cost function, gradient descent'),
    'classification':      ('Python', 'Machine Learning Basics',      'classification algorithms: decision tree, SVM, KNN, Naive Bayes, random forest'),
    'overfitting':         ('Python', 'Machine Learning Basics',      'overfitting vs underfitting, regularization: L1/L2, dropout, cross-validation'),
}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: MULTI-TOPIC MAP
# keyword → list of (topic, subtopic, description)
# When a concept genuinely belongs to multiple topics, we return all of them
# so the user can pick context from a small inline picker.
# ═══════════════════════════════════════════════════════════════════════════

MULTI_TOPIC_MAP = {
    'recursion': [
        ('Algorithms',       'Recursion',        'recursive algorithms, base case, recursive tree, tail recursion, complexity of recursive functions'),
        ('C',                'Functions',        'recursive functions in C, stack frames, factorial, fibonacci, tower of Hanoi in C'),
        ('Java',             'OOP Concepts',     'recursion in Java, recursive methods, call stack, examples: tree traversal, DFS'),
        ('Python',           'Functions & Lambda','recursive functions in Python, sys.setrecursionlimit, examples: quicksort, tree problems'),
        ('Data Structures',  'Trees (Binary, BST)','tree traversal using recursion, inorder/preorder/postorder, recursive tree problems'),
    ],
    'sorting algorithm': [
        ('Algorithms',       'Sorting Algorithms','all sorting algorithms: bubble, merge, quick, heap, radix; time/space complexity'),
        ('C',                'Arrays',            'sorting arrays in C: bubble sort, selection sort implementation'),
        ('Java',             'Collections Framework','Arrays.sort, Collections.sort, Comparator, comparable interface in Java'),
        ('Python',           'Lists & Tuples',    'sorted(), list.sort(), key parameter, custom sort in Python'),
    ],
    'sorting': [
        ('Algorithms',       'Sorting Algorithms','all sorting algorithms: bubble, merge, quick, heap, radix; time/space complexity'),
        ('C',                'Arrays',            'sorting arrays in C: bubble sort, selection sort, qsort()'),
        ('Java',             'Collections Framework','Arrays.sort, Collections.sort, Comparator interface'),
        ('Python',           'Lists & Tuples',    'sorted(), list.sort(), custom comparator, stability of sort'),
    ],
    'exception handling': [
        ('Java',             'Exception Handling','try-catch-finally, checked/unchecked exceptions, custom exceptions, throws keyword'),
        ('Python',           'Exception Handling','try-except-finally, raising exceptions, custom exception classes, context managers'),
        ('C++',              'Exception Handling','try-catch, throw, exception hierarchy, standard exceptions in C++'),
    ],
    'file handling': [
        ('C',                'File Handling',     'fopen, fclose, fread, fwrite, fprintf, fscanf, file modes in C'),
        ('Java',             'Java 8 Features',   'FileReader, FileWriter, BufferedReader, Scanner, NIO files in Java'),
        ('Python',           'File Handling',     'open(), read/write/append modes, with statement, CSV handling in Python'),
    ],
    'linked list': [
        ('Data Structures',  'Linked Lists',      'singly, doubly, circular; insertion, deletion, reversal, cycle detection'),
        ('C',                'Pointers',          'linked list implementation using pointers in C, struct-based nodes'),
        ('Java',             'Collections Framework','LinkedList class in Java, Deque interface, comparison with ArrayList'),
        ('Python',           'OOP in Python',     'implementing linked list in Python using classes, custom node class'),
    ],
    'tree': [
        ('Data Structures',  'Trees (Binary, BST)','binary tree, BST, AVL, Red-Black tree; traversals, height, diameter'),
        ('Algorithms',       'Graph Algorithms',  'spanning trees, minimum spanning tree, tree in graph theory'),
        ('DBMS',             'Indexing',          'B-tree and B+ tree indexing in databases, tree structure for indexes'),
    ],
    'pointer': [
        ('C',                'Pointers',          'pointer basics, pointer arithmetic, pointer to pointer, void pointer, function pointer'),
        ('C++',              'Classes & Objects', 'this pointer, pointers to objects, smart pointers: unique_ptr, shared_ptr'),
    ],
    'pointer arithmetic': [
        ('C',                'Pointers',          'pointer arithmetic, incrementing pointers, array-pointer relationship in C'),
        ('C++',              'Classes & Objects', 'pointer arithmetic in C++, iterator arithmetic'),
    ],
    'multithreading': [
        ('Java',             'Multithreading',    'Thread class, Runnable, synchronized, wait/notify, ExecutorService in Java'),
        ('Python',           'Modules & Packages','threading module, GIL, multiprocessing, concurrent.futures in Python'),
        ('OS',               'Threads',           'user/kernel threads, thread scheduling, thread synchronization, race conditions'),
        ('C++',              'Templates',         'std::thread, mutex, lock_guard, condition_variable in C++'),
    ],
    'array': [
        ('C',                'Arrays',            'array declaration, 1D/2D arrays, passing arrays to functions, string as char array'),
        ('Java',             'Collections Framework','arrays in Java, Arrays class, array vs ArrayList, multidimensional arrays'),
        ('Python',           'Lists & Tuples',    'lists as dynamic arrays in Python, NumPy arrays, list operations'),
        ('Data Structures',  'Arrays',            'array operations, time complexity, dynamic arrays, circular arrays'),
    ],
    'string': [
        ('C',                'Arrays',            'string as char array in C, string functions: strlen, strcpy, strcat, strcmp'),
        ('Java',             'OOP Concepts',      'String class in Java, StringBuilder, StringBuffer, immutability, string pool'),
        ('Python',           'Data Types & Variables','string methods in Python, slicing, formatting, f-strings, raw strings'),
        ('Data Structures',  'Hashing',           'string hashing, rolling hash, string matching algorithms: KMP, Rabin-Karp'),
    ],
    'class': [
        ('Java',             'Classes & Objects', 'class definition, constructors, access modifiers, static members in Java'),
        ('Python',           'OOP in Python',     'class definition, __init__, self, class vs instance variables in Python'),
        ('C++',              'Classes & Objects', 'class vs struct in C++, access specifiers, member functions, friend functions'),
        ('OOP',              'Classes & Objects', 'OOP concept of class, object, instantiation, responsibilities of a class'),
    ],
    'constructor': [
        ('Java',             'Classes & Objects', 'constructor overloading, this(), super(), default constructor, copy constructor'),
        ('Python',           'OOP in Python',     '__init__ method, __new__, constructor behavior in Python'),
        ('C++',              'Constructors & Destructors','constructor types, copy constructor, move constructor, destructor in C++'),
    ],
    'interface': [
        ('Java',             'OOP Concepts',      'interface vs abstract class, default methods, functional interfaces, multiple inheritance'),
        ('OOP',              'Interfaces',         'interface concept, contract, implementation, difference from abstract class'),
        ('C++',              'Classes & Objects', 'pure virtual functions as interfaces in C++, abstract base class'),
    ],
    'operator overloading': [
        ('C++',              'Operator Overloading','overloading +,-,*,/, comparison, stream operators, rules of overloading'),
        ('Python',           'OOP in Python',     'dunder methods: __add__, __eq__, __str__, __len__ for operator overloading'),
    ],
    'lambda': [
        ('Python',           'Functions & Lambda','lambda expressions in Python, map, filter, reduce with lambda'),
        ('Java',             'Java 8 Features',   'lambda expressions, functional interfaces, method references in Java 8'),
        ('C++',              'Templates',         'lambda functions in C++11, capture list, auto parameters'),
    ],
    'closure': [
        ('Python',           'Functions & Lambda','closures in Python, nonlocal keyword, factory functions'),
        ('Java',             'Java 8 Features',   'closures via lambda in Java, effectively final variables'),
        ('JavaScript',       'DOM Manipulation',  'closures in JavaScript, lexical scoping, common use cases'),
    ],
    'generator': [
        ('Python',           'Functions & Lambda','generators in Python, yield keyword, generator expressions, lazy evaluation'),
        ('Java',             'Java 8 Features',   'Stream API as lazy sequences, similar concept to generators'),
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: NOISE WORDS (reject these — not topics)
# ═══════════════════════════════════════════════════════════════════════════

NOISE_WORDS = {
    'test','quiz','exam','question','answer','study','learn','help',
    'chapter','unit','lesson','subject','course','tutorial','notes',
    'abc','xyz','asdf','qwerty','hello','hi','hey','ok','okay',
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','o','p','q','r','s','t','u','v','w','x','y','z',
    'what','how','why','when','where','who','which','this','that',
    'good','bad','easy','hard','difficult','simple','basic','advanced',
    'one','two','three','four','five','six','seven','eight','nine','ten',
}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: CORE RESOLVER
# ═══════════════════════════════════════════════════════════════════════════

def resolve_topic(user_input: str) -> dict:
    """
    Resolves a user's search input to the correct topic/subtopic.

    Returns a dict with:
        status: 'single'   → one definitive match, go directly to quiz
                'multi'    → multiple contexts, show picker to user
                'new'      → genuinely new topic, add silently and quiz
                'invalid'  → not a real topic, show friendly error

        For 'single':
            topic, subtopic, ai_context, display_label

        For 'multi':
            options: list of {topic, subtopic, ai_context, display_label}

        For 'new':
            topic (= user input, title-cased), ai_context

        For 'invalid':
            message
    """
    raw   = user_input.strip()
    clean = raw.lower()
    clean = re.sub(r'\s+', ' ', clean)   # normalise spaces

    # ── 1. Reject empty / too short ───────────────────────────────────────
    if len(clean) < 2:
        return {'status': 'invalid', 'message': 'Please type at least 2 characters.'}

    # ── 2. Reject noise words ─────────────────────────────────────────────
    if clean in NOISE_WORDS:
        return {'status': 'invalid', 'message': f'"{raw}" is too generic to be a topic.'}

    # ── 3. Check multi-topic map (exact) ──────────────────────────────────
    if clean in MULTI_TOPIC_MAP:
        options = []
        for (topic, subtopic, ctx) in MULTI_TOPIC_MAP[clean]:
            options.append({
                'topic':         topic,
                'subtopic':      subtopic,
                'ai_context':    ctx,
                'display_label': f'{topic} → {subtopic}',
            })
        return {'status': 'multi', 'options': options, 'query': raw}

    # ── 4. Check multi-topic map (partial / contained) ────────────────────
    for key, entries in MULTI_TOPIC_MAP.items():
        if key in clean or clean in key:
            options = []
            for (topic, subtopic, ctx) in entries:
                options.append({
                    'topic':         topic,
                    'subtopic':      subtopic,
                    'ai_context':    ctx,
                    'display_label': f'{topic} → {subtopic}',
                })
            return {'status': 'multi', 'options': options, 'query': raw}

    # ── 5. Check alias map (exact) ────────────────────────────────────────
    if clean in ALIAS_MAP:
        topic, subtopic, ctx = ALIAS_MAP[clean]
        return {
            'status':      'single',
            'topic':       topic,
            'subtopic':    subtopic,
            'ai_context':  ctx,
            'display_label': f'{topic} → {subtopic}',
        }

    # ── 6. Check alias map (partial match) ────────────────────────────────
    best = None
    best_score = 0
    for key, (topic, subtopic, ctx) in ALIAS_MAP.items():
        if key in clean:
            score = len(key)
            if score > best_score:
                best_score = score
                best = (topic, subtopic, ctx)
        elif clean in key and len(clean) >= 4:
            score = len(clean)
            if score > best_score:
                best_score = score
                best = (topic, subtopic, ctx)

    if best:
        topic, subtopic, ctx = best
        return {
            'status':        'single',
            'topic':         topic,
            'subtopic':      subtopic,
            'ai_context':    ctx,
            'display_label': f'{topic} → {subtopic}',
        }

    # ── 7. Check if it looks like a real technical term ───────────────────
    if not _looks_like_real_topic(clean):
        return {
            'status':  'invalid',
            'message': f'"{raw}" doesn\'t look like a recognisable topic. Try being more specific.',
        }

    # ── 8. Genuinely new topic — add silently ────────────────────────────
    title_cased = raw.title()
    return {
        'status':      'new',
        'topic':       title_cased,
        'ai_context':  f'{title_cased} — core concepts, fundamentals, and applied problems',
    }


def _looks_like_real_topic(text: str) -> bool:
    """
    Heuristic check: does this string look like it could be a real topic?
    Rejects random gibberish, single letters, purely numeric strings, etc.
    """
    # All digits → not a topic
    if text.replace(' ', '').isdigit():
        return False
    # Only 1-2 chars → too short
    if len(text.replace(' ', '')) <= 2:
        return False
    # Repeated characters like 'aaaaaa' → gibberish
    if len(set(text.replace(' ', ''))) <= 2 and len(text) > 4:
        return False
    # Has at least one real letter
    if not re.search(r'[a-z]', text):
        return False
    # Consonant cluster heuristic (e.g. 'qwrts' has no vowels → gibberish)
    words = text.split()
    for word in words:
        if len(word) > 4:
            vowels = sum(1 for c in word if c in 'aeiou')
            if vowels == 0:
                return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: AI CONTEXT BUILDER
# Called from ai_question_generator to enrich the prompt
# ═══════════════════════════════════════════════════════════════════════════

def build_ai_context(topic: str, subtopic: str, ai_context: str = '') -> str:
    """
    Returns a rich context string to inject into the AI prompt so questions
    are about the right concept, not just the keyword.

    Usage in ai_question_generator.py — replace the simple topic/subtopic
    in the prompt with this enriched context string.
    """
    if ai_context:
        return (
            f"Topic: {topic}\n"
            f"Subtopic: {subtopic}\n"
            f"Context: Generate questions specifically about {ai_context}. "
            f"Do NOT generate generic questions about the word '{subtopic.split()[0]}' — "
            f"focus strictly on the placement/aptitude/CS context described above."
        )
    return f"Topic: {topic}\nSubtopic: {subtopic}"