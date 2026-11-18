module doxygen_module
  !! Module documentation.
  implicit none
contains
  !> Does the thing.
  function documented(x) result(y)
    integer, intent(in) :: x
    integer :: y
    y = x
  end function
end module
