<template>
  <div>
    <!-- buttons -->
    <div class="p-4">
      <button class="btn btn-primary">primary</button>
      <button class="btn btn-secondary">secondary</button>
      <button class="btn btn-accent">accent</button>
    </div>

    <!-- same buttons with another theme! -->
    <div class="p-4" data-theme="abyss">
      <button class="btn btn-primary">Primary</button>
      <button class="btn btn-secondary">Secondary</button>
      <button class="btn btn-accent">Accent</button>
    </div>
    <div class="p-4" data-theme="purplewind">
      <button class="btn btn-primary">Primary</button>
      <button class="btn btn-secondary">Secondary</button>
      <button class="btn btn-accent">Accent</button>
    </div>

    <!-- tab -->
    <div class="tabs tabs-lift p-4">
      <button class="tab">Tab 1</button>
      <button class="tab tab-active">Tab 2</button>
      <button class="tab">Tab 3</button>
      <button class="tab"></button>
    </div>

    <!-- toggle, checkbox, radio -->
    <div class="p-4">
      <input type="checkbox" class="toggle" />
      <input type="checkbox" class="toggle toggle-primary" />
      <input type="checkbox" class="toggle toggle-secondary" />
      <input type="checkbox" class="toggle toggle-accent" />
      <br />
      <input type="checkbox" class="checkbox" />
      <input type="checkbox" class="checkbox-primary checkbox" />
      <input type="checkbox" class="checkbox-secondary checkbox" />
      <input type="checkbox" class="checkbox-accent checkbox" />
      <br />
      <input type="radio" name="radio" class="radio" />
      <input type="radio" name="radio" class="radio-primary radio" />
      <input type="radio" name="radio" class="radio-secondary radio" />
      <input type="radio" name="radio" class="radio-accent radio" />
    </div>

    <!-- card -->
    <div class="card m-4 w-80 shadow-sm">
      <figure>
        <img src="https://img.daisyui.com/images/blog/daisyui-5.webp" />
      </figure>
      <div class="card-body">
        <h2 class="card-title">DaisyUI 5.0</h2>
        <p>
          Rerum reiciendis beatae tenetur excepturi aut pariatur est eos. Sit sit necessitatibus.
        </p>
      </div>
    </div>

    <!-- dropdown -->
    <details class="dropdown m-4">
      <summary class="btn m-1">open/close dropdown</summary>
      <ul class="dropdown-content menu z-[2] w-52 rounded-box bg-base-200 p-2">
        <li><a>Item 1</a></li>
        <li><a>Item 2</a></li>
      </ul>
    </details>

    <!-- Open the modal using ID.showModal() method -->
    <button class="btn" onclick="my_modal_1.showModal()">open modal</button>
    <dialog id="my_modal_1" class="modal">
      <form method="dialog" class="modal-box">
        <p class="py-4">Press ESC key or click the button below to close</p>
        <div class="modal-action">
          <button class="btn">Close</button>
        </div>
      </form>
    </dialog>

    <!-- steps -->
    <ul class="steps my-4 w-full">
      <li class="step step-primary">Register</li>
      <li class="step step-primary">Choose plan</li>
      <li class="step">Purchase</li>
      <li class="step">Receive Product</li>
    </ul>

    <!-- chat bubble -->
    <div class="chat chat-start m-4">
      <div class="avatar chat-image">
        <div class="w-10 rounded-full">
          <img src="https://img.daisyui.com/images/profile/people/pouya-saadeghi.webp" />
        </div>
      </div>
      <div class="chat-bubble">
        see all components
        <a class="link" target="_blank" href="https://daisyui.com/components">Here</a>
      </div>
    </div>
  </div>
</template>
