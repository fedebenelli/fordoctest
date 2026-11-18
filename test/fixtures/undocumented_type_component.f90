module m
  !! Module documentation.
  type :: t
    !! Type documentation.
    integer :: c
  contains
    procedure :: p !! Bound procedure documentation.
  end type
contains
  subroutine p(self)
    !! Procedure documentation.
    class(t) :: self !! Self documentation.
  end subroutine
end module
