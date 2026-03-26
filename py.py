
print("""
╔═════╦═════╦══╗ 
║██   ║     ║  ║ 
╠══╗  ║  ╥  ╨  ║ 
║  ║     ║     ║ 
║  ╠═════╩══╗  ║ 
║  ║        ║  ║ 
║  ╨  ╥  ╥  ║  ║ 
║     ║  ║  ║  ║ 
║  ╞══╣  ╚══╝  ║ 
║     ║      ██║ 
╚═════╩════════╝
	  """)
    import os
    # os.system("clear")
    path = False
    main(0)
    print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")
    while True:
        inpu = get_char()
        if inpu in ["q" , 'Q']:
            exit(0)
        elif inpu in ["r", "R"]:
            # os.system("clear")
            main(1)
            print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")

            path = False
        elif inpu in ["p", "P"]:
            if path == False:
                # os.system("clear")
                main(1)
                print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")
                path = True