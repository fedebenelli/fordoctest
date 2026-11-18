module doxygen_module
  !! Module documentation.
  implicit none
contains
  !> Does the thing.
  !!
  !! @param x Input value.
  function documented(x) result(y)
    integer, intent(in) :: x
    integer :: y
    y = x
  end function

  !> Does another thing.
  !!
  !! @param x Input value.
  subroutine also_documented(x)
    integer, intent(in) :: x
  end subroutine
end module
