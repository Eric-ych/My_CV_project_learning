# todo.py —— 一个最简单的命令行待办事项工具
# 纯新手起步版:所有代码都在这一个文件里,先让它跑起来。

# 我们把任务存在一个文本文件里,这样关掉程序后任务不会丢。
TASK_FILE = "tasks.txt"


def load_tasks():
    """从文件里读出所有任务,返回一个列表。"""
    try:
        # 打开文件,按行读取
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            # 去掉每行末尾的换行符,忽略空行
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # 如果文件还不存在(第一次运行),就返回一个空列表
        return []


def save_tasks(tasks):
    """把任务列表写回文件。"""
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(task + "\n")


def show_tasks(tasks):
    """把所有任务打印出来,前面带编号。"""
    if not tasks:
        print("(还没有任务)")
        return
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task}")


def main():
    """主循环:不停地问用户要做什么,直到用户选择退出。"""
    print("=== 我的待办事项 ===")

    while True:
        # 每次循环都重新读一遍任务,保证是最新的
        tasks = load_tasks()

        print("\n请选择操作:")
        print("  1 - 查看所有任务")
        print("  2 - 添加任务")
        print("  3 - 删除任务")
        print("  4 - 退出")

        choice = input("输入数字并回车: ").strip()

        if choice == "1":
            show_tasks(tasks)

        elif choice == "2":
            new_task = input("要添加的任务内容: ").strip()
            if new_task:
                tasks.append(new_task)
                save_tasks(tasks)
                print("已添加!")
            else:
                print("内容不能为空。")

        elif choice == "3":
            show_tasks(tasks)
            if tasks:
                num = input("输入要删除的任务编号: ").strip()
                # 检查用户输入的是不是有效数字
                if num.isdigit() and 1 <= int(num) <= len(tasks):
                    removed = tasks.pop(int(num) - 1)
                    save_tasks(tasks)
                    print(f"已删除: {removed}")
                else:
                    print("编号无效。")

        elif choice == "4":
            print("再见!")
            break  # 跳出 while 循环,程序结束

        else:
            print("没听懂,请输入 1 到 4 之间的数字。")


# 这一行的意思是:只有直接运行这个文件时,才执行 main()
if __name__ == "__main__":
    main()
