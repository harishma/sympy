"""The definition of the base geometrical entity with attributes common to all
derived geometrical entities.

Contains
--------
GeometryEntity

"""

# How entities are ordered; used by __cmp__ in GeometryEntity
ordering_of_classes = [
    "Point",
    "Segment",
    "Ray",
    "Line",
    "Triangle",
    "RegularPolygon",
    "Polygon",
    "Circle",
    "Ellipse",
    "Curve"
]

class GeometryEntity(tuple):
    """The base class for all geometrical entities.

    This class doesn't represent any particular geometric entity, it only
    provides the implementation of some methods common to all subclasses.

    """

    def __new__(cls, *args, **kwargs):
        return tuple.__new__(cls, args)

    def __getnewargs__(self):
        return tuple(self)

    def intersection(self, o):
        """
        Returns a list of all of the intersections of self with o.

        Notes:
        ======
            - This method is not intended to be used directly but rather
              through the intersection() method or the function found in
              util.py.
            - An entity is not required to implement this method.
            - If two different types of entities can intersect, the item with
              higher index in ordering_of_classes should implement
              intersections with anything having a lower index.

        """
        raise NotImplementedError()

    def encloses(self, o):
        """
        Return True if o is inside (not on or outside) the boundaries of self.

        The object will be decomposed into Points and individual Entities need
        only define an encloses_point method for their class.
        """
        from sympy.geometry.point import Point
        from sympy.geometry.line import Segment, Ray, Line
        from sympy.geometry.ellipse import Circle, Ellipse
        from sympy.geometry.polygon import Polygon, RegularPolygon

        if isinstance(o, Point):
            return self.encloses_point(o)
        elif isinstance(o, Segment):
            return all(self.encloses_point(x) for x in o.points)
        elif isinstance(o, Ray) or isinstance(o, Line):
            return False
        elif isinstance(o, Ellipse):
            return self.encloses_point(o.center) and not self.intersection(o)
        elif isinstance(o, Polygon):
            if isinstance(o, RegularPolygon):
                if not self.encloses_point(o.center):
                    return False
            return all(self.encloses_point(v) for v in o.vertices)
        raise NotImplementedError()

    def is_similar(self, other):
        """Is this geometrical entity similar to another geometrical entity?

        Two entities are similar if a uniform scaling (enlarging or
        shrinking) of one of the entities will allow one to obtain the other.

        Notes
        -----
        This method is not intended to be used directly but rather
        through the `are_similar` function found in util.py.
        An entity is not required to implement this method.
        If two different types of entities can be similar, it is only
        required that one of them be able to determine this.

        """
        raise NotImplementedError()

    @staticmethod
    def extract_entities(args, remove_duplicates=True):
        """Extract all GeometryEntity instances from a sequence of objects.

        Parameters
        ----------
        args : a (possibly nested) sequence of objects
        remove_duplicates : boolean, optional
            Duplicate entities are removed from the result (default is True).

        Returns
        -------
        entities : tuple of GeometryEntity.

        Notes
        -----
        The extraction is performed recursively - a GeometryEntity in a
        sub-sequences will be added to the result.
        Anything that is not a GeometryEntity instance is excluded from the
        return value.
        Ordering of arguments is always maintained. If duplicates
        are removed then the entry with the lowest index is kept.

        """
        ret = list()
        for arg in args:
            if isinstance(arg, GeometryEntity):
                ret.append(arg)
            elif isinstance(arg, (list, tuple, set)):
                ret.extend(GeometryEntity.extract_entities(arg))
        if remove_duplicates:
            temp = set(ret)
            ind, n = 0, len(ret)
            for counter in xrange(n):
                x = ret[ind]
                if x in temp:
                    temp.remove(x)
                    ind += 1
                else:
                    del ret[ind]
        return tuple(ret)

    def subs(self, old, new):
        if hasattr(self, '_eval_subs_'):
            return self.subs(old, new)
        elif isinstance(self, GeometryEntity):
            return type(self)(*[a.subs(old, new) for a in self])
        else:
            return self

    @property
    def args(self):
        return tuple(self)

    def __ne__(self, o):
        """Test inequality of two geometrical entities."""
        return not self.__eq__(o)

    def __radd__(self, a):
        return a.__add__(self)

    def __rsub__(self, a):
        return a.__sub__(self)

    def __rmul__(self, a):
        return a.__mul__(self)

    def __rdiv__(self, a):
        return a.__div__(self)

    def __str__(self):
        """String representation of a GeometryEntity."""
        from sympy.printing import sstr
        return type(self).__name__ + sstr(tuple(self))

    def __repr__(self):
        """String representation of a GeometryEntity that can be evaluated
        by sympy."""
        return type(self).__name__ + repr(tuple(self))

    def __cmp__(self, other):
        """Comparison of two GeometryEntities."""
        n1 = self.__class__.__name__
        n2 = other.__class__.__name__
        c = cmp(n1, n2)
        if not c:
            return 0

        i1 = -1
        for cls in self.__class__.__mro__:
            try:
                i1 = ordering_of_classes.index(cls.__name__)
                break
            except ValueError:
                i1 = -1
        if i1 == -1:
            return c

        i2 = -1
        for cls in other.__class__.__mro__:
            try:
                i2 = ordering_of_classes.index(cls.__name__)
                break
            except ValueError:
                i2 = -1
        if i2 == -1:
            return c

        return cmp(i1, i2)
