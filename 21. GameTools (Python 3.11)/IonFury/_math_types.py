class Vec2:
    def __init__ (self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__ (self):
        return f'{ self.__class__.__name__ }({ self.x }, { self.y })'

    def __iter__ (self):
        return iter([
            self.x,
            self.y
        ])

    def __add__ (self, rhs):
        assert isinstance(rhs, Vec2)

        return Vec3(
            self.x + rhs.x,
            self.y + rhs.y,
        )

class Vec3:
    def __init__ (self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__ (self):
        return f'{ self.__class__.__name__ }({ self.x }, { self.y }, { self.z })'

    def __iter__ (self):
        return iter([
            self.x,
            self.y,
            self.z
        ])

    def __add__ (self, rhs):
        assert isinstance(rhs, Vec3)

        return Vec3(
            self.x + rhs.x,
            self.y + rhs.y,
            self.z + rhs.z,
        )


if __name__ == '__main__':
    v = Vec3(100, 20, 30)
    print(sorted(v))