

# Function Development






# Refactor
- [x] Replace '<<' with '>>'
- [x] Power.out -> Power.O
- [x] Implement testcases with assert functions
- [x] Replace Merge with Branch
- [x] I0, I1 -> I[0], I[1]
- [x] Remove Gate class
- [x] Correct Selector16to1.__repr__
- [x] Update SimulatedCircuit: Either step() or update_sequence
- [x] Update Branch: act like Port
- [x] Reimplement Split with Branch
- [x] Split.O0/O1 -> O[0], O[1]
- [x] Branch >> (p1, p2, p3)
- [x] Pythonic code: for..append -> extend
- [x] nmem -> ncell?
- [x] Combine RAM256x8, RAM4096x8
- [ ] aaa.O >> bbb.I -> aaa >> bbb
- [ ] Generalize Gate like And -> AndN
- [ ] Add function descriptions



# unittest template
    suite = unittest.TestSuite()
    suite.addTests([
        Test(''),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)