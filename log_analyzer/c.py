from log_analyzer.analyzer import LogAnalyzer


def check():
    log_dir = r"C:\Users\yonzr\Desktop\Yehonatan\My_projects\Nvidia\Logs"
    config_file = r"C:\Users\yonzr\Desktop\Yehonatan\My_projects\Nvidia\Logs\events.txt"
    LogAnalyzer(log_dir, config_file).run()


check()
