import random
import re

def filted(input_string, words_to_replace):
    replacements = ['_filted_', '_已过滤_']
    outputstring = input_string

    for word in words_to_replace:
        # 查找所有匹配的词
        for match in re.finditer(re.escape(word), outputstring):
            # 选择一个随机的替换字
            replacement_char = random.choice(replacements)
            # 生成与原词等长的替换字符串
            replacement_word = replacement_char
            # 替换匹配的词
            outputstring = outputstring[:match.start()] + replacement_word + outputstring[match.end():]

    return outputstring

if __name__=="__main__":
    # 示例输入
    input_string = "苹果香蕉 橙子 苹果 梨"
    words_to_replace = ["苹果", "香蕉", "橙子"]
    # 调用函数并打印结果
    result=filted(input_string, words_to_replace)
    print(result)
