module m
  !! Module documentation.
  interface
    !! Interface documentation.
    module subroutine p()
    end subroutine
  end interface
end module

submodule (m) sm
contains
  module procedure p
  end procedure
end submodule
