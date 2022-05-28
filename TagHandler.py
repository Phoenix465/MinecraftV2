#  https://stackoverflow.com/questions/41834530/how-to-make-python-decorators-work-like-a-tag-to-make-function-calls-by-tag

import functools


class TagDecorator(object):
    def __init__(self, tagName):
        self.tagName = tagName

    def __str__(self):
        return "<TagDecorator {tagName}>".format(tagName=self.tagName)

    def __call__(self, f, *args, **kwargs):
        if hasattr(f, "_tags"):
            f._tags.append(self.tagName)
        else:
            f._tags = [self.tagName]

        return f


class TagDecoratorClass(object):
    def __init__(self, className):
        self.className = className

    def __call__(self, cls):
        cls._tagged = True
        taggedFunctions = []

        for method in cls.__dict__.values():
            if hasattr(method, "_tags"):
                taggedFunctions.append(method)
        cls.taggedFunctions = taggedFunctions

        return cls


@functools.lru_cache(maxsize=None)  # memoization
def FunctionTag(tagName):
    return TagDecorator(tagName)


@functools.lru_cache(maxsize=None)  # memoization
def ClassTag(className):
    return TagDecoratorClass(className)